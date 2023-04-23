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
                ]
            }
        )
    ]
)
def test_query_resource(urls, expected):
    client = Client()
    response = client.get(urls)
    assert expected == response.json()
