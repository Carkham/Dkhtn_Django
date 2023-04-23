import json
from datetime import datetime

import pika
import pytest
from config.settings.base import rabbitmq_host
from django.test import Client
from dkhtn_django.log.log_parser import LogParser, LogMessage

_timestamp = datetime.strptime("2023-04-15 16:40:48", "%Y-%m-%d %H:%M:%S")


@pytest.fixture()
def parser():
    return LogParser()


@pytest.mark.parametrize(
    "data, expected",
    [
        (
            "2023-04-15 16:40:48 | ${function id} | INFO 	- This is a info",
            {
                "timestamp": _timestamp,
                "function_id": "${function id}",
                "level": "INFO",
                "message": "This is a info"
            }
        ),
        (
            "2023-04-15 16:40:48 | ${function id} | ERROR 	- This is a error",
            {
                "timestamp": _timestamp,
                "function_id": "${function id}",
                "level": "ERROR",
                "message": "This is a error"
            }
        ),
        (
            "2023-04-15 16:40:48 | ${function id} | WARNING 	- This is a warning",
            {
                "timestamp": _timestamp,
                "function_id": "${function id}",
                "level": "WARNING",
                "message": "This is a warning"
            }
        ),
    ]
)
def test_parse_log(data, expected, parser):
    log_message = parser.parse_log(data)
    for key in expected:
        assert getattr(log_message, key) == expected[key]


@pytest.mark.django_db
@pytest.mark.parametrize(
    "messages",
    [
        (
            [
                {
                    "timestamp": "2023-04-15 16:40:48",
                    "function_id": "5201314",
                    "level": "WARNING",
                    "message": "This is a warning"
                },
                {
                    "timestamp": "2023-04-15 16:40:48",
                    "function_id": "5201314",
                    "level": "ERROR",
                    "message": "This is a error"
                },
            ]
        )
    ]
)
def test_insert_log(messages):
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()

    channel.queue_declare(queue="log_queue")
    channel.basic_publish(exchange="", routing_key="log_queue", body=json.dumps(messages).encode("utf-8"))
    channel.close()

    expected = LogMessage.objects.all()
    actual = LogMessage.objects.filter(function_id="5201314")
    assert list(expected) == list(actual)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "urls, status, msg, expected",
    [
        (
            "/api/logs/5201314",
            0,
            "",
            {"start_time": None, "end_time": None, "level": None, "keyword": None}
        ),
        (
            "/api/logs/5201314?startDatetime=2023/04/13 12:00&endDatetime=2023-04-15T09:40&keyword=warning",
            -1,
            "Your timestamp format is wrong",
            {}
        ),
        (
            "/api/logs/5201314?endDatetime=2023-04-15T09:40&level=WARNING",
            0,
            "",
            {"start_time": None, "end_time": "2023-04-15T09:40", "level": "WARNING", "keyword": None}
        ),
        (
            "/api/logs/5201314?startDatetime=2023-04-12T12:00&endDatetime=2023-04-20T19:40&level=WARNING&keyword=warn",
            0,
            "",
            {"start_time": "2023-04-12T12:00", "end_time": "2023-04-20T19:40", "level": "WARNING", "keyword": "warn"}
        ),
    ]
)
def test_query_log(urls, status, msg, expected):
    client = Client()
    response = client.get(urls).json()
    assert response["code"] == status
    assert response["msg"] == msg
    for log in response["data"]["logs"]:
        if expected["level"] is not None:
            assert log["level"] == expected["level"]
        if expected["keyword"] is not None:
            assert expected["keyword"] in log["content"]
        time = datetime.strptime(log["timestamp"], "%Y-%m-%dT%H:%M")
        if expected["end_time"] is not None:
            end_time = datetime.strptime(expected["end_time"], "%Y-%m-%dT%H:%M")
        else:
            end_time = datetime.now().strftime("%Y-%m-%dT%H:%M")
        assert time < end_time
