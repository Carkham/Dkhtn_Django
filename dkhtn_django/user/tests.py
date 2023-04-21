import json

import pytest
from django.test import Client
from django.conf import settings
from dkhtn_django.user.models import User
from dkhtn_django.utils.redis import redis_set

user_number = 1


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
def test_email_check(client, url, info, status_code, info_dict):
    username = "用户名"
    password = "123456"
    avatar = "2"
    email = "邮箱"
    User.objects.create_user(username=username,
                             password=password,
                             avatar=avatar,
                             email=email)
    session_id = "12345"
    redis_set(settings.REDIS_VERIFY, session_id, json.dumps(info), settings.REDIS_VERIFY_TIMEOUT)
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
                "password": "YNZvjmP7g1FY0xl5OmnEFfaYruV0oH8T5lzwbmxhdPKSR25tK1YwfAcbIFCmIWb2mI129w5kOP8qBUBDAbGp5nyw"
                            "C3CCbrRbixkzyOROJ2hE0lQTC1+/R0EYloG1e9mGGRws3+IaUUOXQ0JZkNtg/gzY9qa9w2MLfWfYXYbF1JI="
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
                "password": "YNZvjmP7g1FY0xl5OmnEFfaYruV0oH8T5lzwbmxhdPKSR25tK1YwfAcbIFCmIWb2mI129w5kOP8qBUBDAbGp5nyw"
                            "C3CCbrRbixkzyOROJ2hE0lQTC1+/R0EYloG1e9mGGRws3+IaUUOXQ0JZkNtg/gzY9qa9w2MLfWfYXYbF1JI="
            },
            200,
            {
                "code": 1,
                "message": "用户名或密码错误",
            }
        ),
    ]
)
def test_login(client, url, info, status_code, info_dict):
    global login_session_id
    username = "用户名"
    password = "123456"
    avatar = "2"
    email = "yonghuming"
    User.objects.create_user(username=username,
                             password=password,
                             avatar=avatar,
                             email=email)
    global user_number
    user_number += 1
    if login_session_id is not None:
        client.cookies.__setitem__("session_id", login_session_id)
    response = client.post(url, data=json.dumps(info), content_type='applications/json')
    login_session_id = response.cookies.get("session_id")
    if login_session_id is not None:
        login_session_id = login_session_id.value
    assert response.status_code == status_code
    assert response.json() == info_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, info, status_code, info_dict",
    [
        (
            "/api/user/register",
            {
                "uname": "用户名",
                "avatar": "用户头像",
                "email": "邮箱号",
                "email_sms": "邮箱校验码",
                "password": "YNZvjmP7g1FY0xl5OmnEFfaYruV0oH8T5lzwbmxhdPKSR25tK1YwfAcbIFCmIWb2mI129w5kOP8qBUBDAbGp5nyw"
                            "C3CCbrRbixkzyOROJ2hE0lQTC1+/R0EYloG1e9mGGRws3+IaUUOXQ0JZkNtg/gzY9qa9w2MLfWfYXYbF1JI="
            },
            200,
            {
                "code": 1,
                "message": "邮箱验证码错误或已失效",
            }
        ),
        (
            "/api/user/register",
            {
                "uname": "用户名",
                "avatar": "用户头像",
                "email": "邮箱号2",
                "email_sms": "邮箱验证码2233",
                "password": "YNZvjmP7g1FY0xl5OmnEFfaYruV0oH8T5lzwbmxhdPKSR25tK1YwfAcbIFCmIWb2mI129w5kOP8qBUBDAbGp5nyw"
                            "C3CCbrRbixkzyOROJ2hE0lQTC1+/R0EYloG1e9mGGRws3+IaUUOXQ0JZkNtg/gzY9qa9w2MLfWfYXYbF1JI="
            },
            200,
            {
                "code": 2,
                "message": "用户名已存在",
            }
        ),
        (
            "/api/user/register",
            {
                "uname": "用户名2",
                "avatar": "用户头像",
                "email": "邮箱号",
                "email_sms": "邮箱验证码2233",
                "password": "YNZvjmP7g1FY0xl5OmnEFfaYruV0oH8T5lzwbmxhdPKSR25tK1YwfAcbIFCmIWb2mI129w5kOP8qBUBDAbGp5nyw"
                            "C3CCbrRbixkzyOROJ2hE0lQTC1+/R0EYloG1e9mGGRws3+IaUUOXQ0JZkNtg/gzY9qa9w2MLfWfYXYbF1JI="
            },
            200,
            {
                "code": 3,
                "message": "邮箱已存在",
            }
        ),
        (
            "/api/user/register",
            {
                "uname": "用户名2",
                "avatar": "用户头像",
                "email": "邮箱号2",
                "email_sms": "邮箱验证码2233",
                "password": "YNZvjmP7g1FY0xl5OmnEFfaYruV0oH8T5lzwbmxhdPKSR25tK1YwfAcbIFCmIWb2mI129w5kOP8qBUBDAbGp5nyw"
                            "C3CCbrRbixkzyOROJ2hE0lQTC1+/R0EYloG1e9mGGRws3+IaUUOXQ0JZkNtg/gzY9qa9w2MLfWfYXYbF1JI="
            },
            200,
            {
                "code": 0,
                "message": "注册成功",
            }
        ),
    ]
)
def test_register(client, url, info, status_code, info_dict):
    session_id = "register_test"
    redis_set(settings.REDIS_VERIFY, session_id, "邮箱验证码2233", settings.REDIS_VERIFY_TIMEOUT)
    username = "用户名"
    password = "123456"
    avatar = "2"
    email = "邮箱号"
    User.objects.create_user(username=username,
                             password=password,
                             avatar=avatar,
                             email=email)
    global user_number
    user_number += 1
    client.cookies.__setitem__("session_id", session_id)
    response = client.post(url, data=json.dumps(info), content_type='applications/json')
    assert response.status_code == status_code
    assert response.json() == info_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, status_code, info_dict",
    [
        (
            "/api/user/info",
            200,
            {
                "code": 1,
                "message": "用户未登录"
            }
        ),
    ]
)
def test_userinfo_logout_without_session_id(client, url, status_code, info_dict):
    response = client.get(url)
    assert response.status_code == status_code
    assert response.json() == info_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, status_code, info_dict",
    [
        (
            "/api/user/info",
            200,
            {
                "code": 1,
                "message": "用户未登录"
            }
        ),
    ]
)
def test_userinfo_logout_with_session_id(client, url, status_code, info_dict):
    session_id = "userinfo_test_logout"
    client.cookies.__setitem__("session_id", session_id)
    response = client.get(url)
    assert response.status_code == status_code
    assert response.json() == info_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, status_code, info_dict",
    [
        (
            "/api/user/info",
            200,
            {
                "code": 0,
                "message": "success",
                "data": {
                    "uname": "用户名",
                    "avatar": "用户头像",
                    "email": "邮箱号",
                }
            }
        ),
    ]
)
def test_userinfo_login(client, url, status_code, info_dict):
    session_id = "userinfo_test"
    redis_set(settings.REDIS_LOGIN, session_id,
              json.dumps({"id": 67, "username": "用户名", "avatar": "用户头像", "email": "邮箱号"}),
              settings.REDIS_TIMEOUT)
    client.cookies.__setitem__("session_id", session_id)
    response = client.get(url)
    assert response.status_code == status_code
    assert response.json() == info_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, info, status_code, info_dict",
    [
        (
            "/api/user/uname-change",
            {
                "uname": "修改后的用户名",
            },
            200,
            {
                "code": 1,
                "message": "用户未登录",
            }
        ),
    ]
)
def test_name_change_logout(client, url, info, status_code, info_dict):
    response = client.post(url, data=json.dumps(info), content_type='applications/json')
    assert response.status_code == status_code
    assert response.json() == info_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, info, status_code, info_dict",
    [
        (
            "/api/user/uname-change",
            {
                "uname": "修改后的用户名",
            },
            200,
            {
                "code": 0,
                "message": "用户名修改成功",
            }
        ),
        (
            "/api/user/uname-change",
            {
                "uname": "修改后的用户名",
            },
            200,
            {
                "code": 3,
                "message": "用户不存在",
            }
        ),
        (
            "/api/user/uname-change",
            {
                "uname": "用户名",
            },
            200,
            {
                "code": 2,
                "message": "用户名已存在",
            }
        ),
    ]
)
def test_name_change_login(client, url, info, status_code, info_dict):
    global user_number
    session_id = "username_change_test"
    User.objects.create_user(username="用户名",
                             password="rsa加密的用户密码字符串",
                             avatar="用户头像",
                             email="邮箱号")
    user_number += 1
    redis_set(settings.REDIS_LOGIN, session_id,
              json.dumps({"id": user_number, "username": "用户名", "avatar": "用户头像", "email": "邮箱号"}),
              settings.REDIS_TIMEOUT)
    user_number -= 1  # 测试修改重名
    client.cookies.__setitem__("session_id", session_id)
    response = client.post(url, data=json.dumps(info), content_type='applications/json')
    assert response.status_code == status_code
    assert response.json() == info_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, info, status_code, info_dict",
    [
        (
            "/api/user/uname-change",
            {
                "uname": "修改后的用户名",
            },
            200,
            {
                "code": 1,
                "message": "用户未登录",
            }
        ),
    ]
)
def test_password_change_logout(client, url, info, status_code, info_dict):
    global user_number
    response = client.post(url, data=json.dumps(info), content_type='applications/json')
    assert response.status_code == status_code
    assert response.json() == info_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, info, status_code, info_dict",
    [
        (
            "/api/user/password-change",
            {
                "password": "修改后的密码",
            },
            200,
            {
                "code": 0,
                "message": "success",
            }
        ),
        (
            "/api/user/password-change",
            {
                "password": "修改后的密码",
            },
            200,
            {
                "code": 2,
                "message": "用户不存在",
            }
        ),
    ]
)
def test_password_change_login(client, url, info, status_code, info_dict):
    global user_number
    session_id = "username_change_test"
    User.objects.create_user(username="用户名",
                             password="rsa加密的用户密码字符串",
                             avatar="用户头像",
                             email="邮箱号")
    redis_set(settings.REDIS_LOGIN, session_id,
              json.dumps({"id": 12, "username": "用户名", "avatar": "用户头像", "email": "邮箱号"}),
              settings.REDIS_TIMEOUT)
    client.cookies.__setitem__("session_id", session_id)
    response = client.post(url, data=json.dumps(info), content_type='applications/json')
    assert response.status_code == status_code
    assert response.json() == info_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, info, status_code, info_dict",
    [
        (
            "/api/user/email-change",
            {
                "email": "修改后的email",
                "email_sms": "邮箱验证码",
            },
            200,
            {
                "code": 1,
                "message": "用户未登录",
            }
        ),
    ]
)
def test_email_change_logout(client, url, info, status_code, info_dict):
    response = client.post(url, data=json.dumps(info), content_type='applications/json')
    assert response.status_code == status_code
    assert response.json() == info_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, info, status_code, info_dict",
    [
        (
            "/api/user/email-change",
            {
                "email": "修改后的email",
                "email_sms": "邮箱验证码",
            },
            200,
            {
                "code": 0,
                "message": "邮箱修改成功",
            }
        ),
        (
            "/api/user/email-change",
            {
                "email": "修改后的email",
                "email_sms": "邮箱验证码",
            },
            200,
            {
                "code": 4,
                "message": "用户不存在",
            }
        ),
        (
            "/api/user/email-change",
            {
                "email": "邮箱号",
                "email_sms": "邮箱验证码",
            },
            200,
            {
                "code": 3,
                "message": "邮箱已存在",
            }
        ),
        (
            "/api/user/email-change",
            {
                "email": "修改后的email",
                "email_sms": "邮箱验证码233",
            },
            200,
            {
                "code": 1,
                "message": "邮箱验证码错误或已失效",
            }
        ),
    ]
)
def test_email_change_login(client, url, info, status_code, info_dict):
    session_id = "12345"
    redis_set(settings.REDIS_VERIFY, session_id, "邮箱验证码", settings.REDIS_VERIFY_TIMEOUT)
    client.cookies.__setitem__("session_id", session_id)
    User.objects.create_user(username="用户名",
                             password="rsa加密的用户密码字符串",
                             avatar="用户头像",
                             email="邮箱号")
    redis_set(settings.REDIS_LOGIN, session_id,
              json.dumps({"id": 14, "username": "用户名", "avatar": "用户头像", "email": "邮箱号"}),
              settings.REDIS_TIMEOUT)
    client.cookies.__setitem__("session_id", session_id)
    response = client.post(url, data=json.dumps(info), content_type='applications/json')
    assert response.status_code == status_code
    assert response.json() == info_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, info, status_code, info_dict",
    [
        (
            "/api/user/avatar-change",
            {
                "avatar": "修改后的用户头像标识",
            },
            200,
            {
                "code": 1,
                "message": "用户未登录",
            }
        ),
    ]
)
def test_avatar_change_logout(client, url, info, status_code, info_dict):
    response = client.post(url, data=json.dumps(info), content_type='applications/json')
    assert response.status_code == status_code
    assert response.json() == info_dict


@pytest.mark.django_db
@pytest.mark.parametrize(
    "url, info, status_code, info_dict",
    [
        (
            "/api/user/avatar-change",
            {
                "avatar": "修改后的",
            },
            200,
            {
                "code": 0,
                "message": "头像修改成功",
            }
        ),
        (
            "/api/user/avatar-change",
            {
                "avatar": "修改后的用户头像标识",
            },
            200,
            {
                "code": 2,
                "message": "用户不存在",
            }
        ),
    ]
)
def test_avatar_change_login(client, url, info, status_code, info_dict):
    session_id = "12345678"
    redis_set(settings.REDIS_LOGIN, session_id,
              json.dumps({"id": 18, "username": "用户名", "avatar": "用户头像", "email": "邮箱号"}),
              settings.REDIS_TIMEOUT)
    User.objects.create_user(username="用户名",
                             password="rsa加密的用户密码字符串",
                             avatar="用户头像",
                             email="邮箱号")
    client.cookies.__setitem__("session_id", session_id)
    response = client.post(url, data=json.dumps(info), content_type='applications/json')
    assert response.status_code == status_code
    assert response.json() == info_dict
