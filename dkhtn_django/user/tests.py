# from django.test import TestCase

# Create your tests here.
import pytest
from django.test import Client
from django.conf import settings


@pytest.fixture()
def client():
    return Client()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "get_url, status_code, info_dict",
    [
        (
            "/api/user/email-send?email=test@test.com",
            200,
            {
                "code": 0,
                "message": "验证码发送成功"
            }
        ),
        (
            "/api/user/email-send",
            200,
            {
                "code": 1,
                "message": "请输入邮箱"
            }
        ),
    ]
)
def test_email_send(client, get_url, status_code, info_dict):
    response = client.get(get_url)
    assert response.status_code == status_code
    assert response.json() == info_dict




@pytest.mark.django_db
@pytest.mark.parametrize(
    "get_url, status_code, info_dict",
    [
        (
            "/api/user/rsa-pub",
            200,
            {
                "code": 0,
                "message": "success",
                "data": settings.RSA_PUBLIC_KEY,
            }
        ),
    ]
)
def test_ras_get(client, get_url, status_code, info_dict):
    response = client.get(get_url)
    assert response.status_code == status_code
    assert response.json() == info_dict
