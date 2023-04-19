import json

import pytest
from django.test import Client
from django.conf import settings
from dkhtn_django.user.models import User
from dkhtn_django.utils.redis_utils import redis_set


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
    "url, info, status_code, info_dict",
    [
        (
            "/api/user/email-check",
            {
                "email": "邮箱",
                "email_sms": "邮箱验证码"
            },
            200,
            {
                "code": 1,
                "message": "邮箱验证码错误或已失效"
            }
        ),
        (
            "/api/user/email-check",
            {
                "email": "邮箱",
                "email_sms": "邮箱验证码2233"
            },
            200,
            {
                "code": 0,
                "message": "success",
            }
        ),
    ]
)
def test_(client, url, info, status_code, info_dict):
    session_id = "12345"
    redis_set(settings.REDIS_DB_VERIFY, session_id, "邮箱验证码2233", settings.REDIS_VERIFY_TIMEOUT)
    client.cookies.__setitem__("session_id", session_id)
    response = client.post(url, data=json.dumps(info), content_type='applications/json')
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


login_session_id = None


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
    global login_session_id
    username = "用户名"
    password = "rsa加密的用户密码字符串"
    avatar = "2"
    email = "yonghuming"
    user = User.objects.create_user(username=username,
                                    password=password,
                                    avatar=avatar,
                                    email=email)
    if login_session_id is not None:
        client.cookies.__setitem__("session_id", login_session_id)
    response = client.post(url, data=json.dumps(info), content_type='applications/json')
    login_session_id = response.cookies.get("session_id")
    if login_session_id is not None:
        login_session_id = login_session_id.value
    assert response.status_code == status_code
    assert response.json() == info_dict
