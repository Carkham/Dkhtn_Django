# Create your tests here.
import pytest
from django.test import Client


@pytest.mark.django_db
@pytest.mark.parametrize(
    "urls, expected",
    [
        (
            "/api/resource/query-resource",
            {
                "code": 0,
                "msg": "",
                "data": [
                    {
                        "func-id": 114514,
                        "state": 1,
                        "cpu": 0,
                        "memory": 0,
                        "run_time": 0,
                        "times": 0,
                        "error": 0,
                        "cost": 0
                    }
                ]
            }
        )
    ]
)
def test_query_resource(urls, expected):
    client = Client()
    response = client.get(urls)
    assert expected == response.json()
