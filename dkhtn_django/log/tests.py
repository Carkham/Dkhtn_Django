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
    "urls, expected",
    [
        (
            "/api/log/5201314",
            {
                "code": -1,
                "msg": "The request does not contain certain keys",
                "data": {"logs": []}
            }
        ),
        (
            "/api/log/5201314?startDatetime=2023/04/13 12:00&endDatetime=2023-04-15T09:40&level=WARNING&keyword=warning",
            {
                "code": -1,
                "msg": "Your timestamp format is not appropriate",
                "data": {"logs": []}
            }
        ),
        (
            "/api/log/5201314?endDatetime=2023-04-15T09:40&level=WARNING&keyword=warning",
            {
                "code": -1,
                "msg": "Your timestamp format is not appropriate",
                "data": {"logs": []}
            }
        ),
        (
            "/api/log/5201314?startDatetime=2023-04-20T12:00&endDatetime=2023-04-20T19:40&level=WARNING&keyword=warning",
            {
                "code": 0,
                "msg": "",
                "data": {"logs": []}
            }
        ),
        (
            "/api/log/5201314?startDatetime=2023-04-12T12:00&endDatetime=2023-04-20T19:40&level=WARNING&keyword=warning",
            {
                "code": 0,
                "msg": "",
                "data": {"logs": [
                    {
                        "level": "WARNING",
                        "timestamp": "2023-04-14 08:40:48",
                        "content": "This is a warning"
                    }
                ]
                }}
        ),
    ]
)
def test_query_log(urls, expected):
    print("test query service")
    client = Client()
    response = client.get(urls)
    assert json.dumps(expected) == response
