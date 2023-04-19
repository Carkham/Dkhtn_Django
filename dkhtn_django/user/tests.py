import json

import pytest
from django.test import Client
from django.conf import settings
from dkhtn_django.user.models import User


@pytest.fixture()
def client():
    return Client()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, status_code, info_dict",
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
def test_email_send(client, url, status_code, info_dict):
    response = client.get(url)
    assert response.status_code == status_code
    assert response.json() == info_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, status_code, info_dict",
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
def test_rsa_get(client, url, status_code, info_dict):
    response = client.get(url)
    assert response.status_code == status_code
    assert response.json() == info_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, info, status_code, info_dict",
    [
        (
            "/api/user/login",
            {
                "uname": "用户名",
                "password": "rsa加密的用户密码字符串"
            },
            200,
            {
                "code": 0,
                "message": "登录成功",
            }
        ),
        (
            "/api/user/login",
            {
                "uname": "yonghuming",
                "password": "rsa加密的用户密码字符串"
            },
            200,
            {
                "code": 0,
                "message": "登录成功",
            }
        ),
        (
            "/api/user/login",
            {
                "uname": "test",
                "password": "test"
            },
            200,
            {
                "code": 1,
                "message": "用户名或邮箱号或密码错误",
            }
        ),
    ]
)
def test_login(client, url, info, status_code, info_dict):
    username = "用户名"
    password = "rsa加密的用户密码字符串"
    avatar = "2"
    email = "yonghuming"
    user = User.objects.create_user(username=username,
                                    password=password,
                                    avatar=avatar,
                                    email=email)
    response = client.post(url, data=json.dumps(info), content_type='applications/json')
    assert response.status_code == status_code
    assert response.json() == info_dict
