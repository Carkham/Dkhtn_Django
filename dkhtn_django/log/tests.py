import pytest
from dkhtn_django.log.log_parser import LogParser
from datetime import datetime

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
