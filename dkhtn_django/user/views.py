import json
import uuid

from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth import authenticate

from .models import User
from .rabbit.RabbitMQ import rabbit_mq
from .wrappers import wrapper_verify_check
from ..utils import redis
from ..utils.log import Log
from ..utils.rsa_decrypt import decrypt


def rsa_get(request):
    """
    获取RSA公钥
    :param request:
    :return: RSA公钥
    """
    response = {
        "code": 0,
        "message": "success",
        "data": settings.RSA_PUBLIC_KEY,
    }
    return JsonResponse(response)


def login(request):
    """
    登录接口，登录完成设置session
    :param request:
    :return: JsonResponse
    """
    try:
        data = json.loads(request.body)
        username = data.get('uname')
        password = decrypt(data.get('password'))
        user = authenticate(username=username, password=password)
        if user is None:
            response = {
                "code": 1,
                "message": "用户名或密码错误",
            }
            return JsonResponse(response)
        else:
            response = {
                "code": 0,
                "message": "登录成功",
            }
            # 更新session
            old_session = redis.redis_get(settings.REDIS_LOGIN, user.id)
            new_session = uuid.uuid4().hex
            if old_session is None:
                session_data = json.dumps(user.get_info())
                redis.redis_set(settings.REDIS_LOGIN, new_session, session_data)
            else:
                redis.redis_update_key(settings.REDIS_LOGIN, old_session, new_session)
            response = JsonResponse(response)
            response.set_cookie("session_id", new_session)
            return response
    except Exception as e:
        Log().error(e.__str__())


def register(request):
    """
    注册，流程为->（前端）先调用获取邮箱验证码接口->（后端）发送验证邮件，建立session id，存储验证码，
    反馈前端->（前端）调用用户注册接口->（后端）检验session id，检验验证码，注册成功则直接登录
    :param request:
    :return:
    """
    try:
        data = json.loads(request.body)
        username = data.get('uname')
        password = decrypt(data.get('password'))
        email = data.get('email')
        avatar = data.get('avatar')
        # 检查重名
        if User.objects.filter(username=username):
            response = {
                "code": 2,
                "message": "用户名已存在",
            }
            return JsonResponse(response)
        # 检查邮箱重复
        if User.objects.filter(email=email):
            response = {
                "code": 3,
                "message": "邮箱已存在",
            }
            return JsonResponse(response)
        # 进行注册
        user = User.objects.create_user(username=username,
                                        password=password,
                                        avatar=avatar,
                                        email=email)
        # 登录信息登记
        response = {
            "code": 0,
            "message": "注册成功",
        }
        session_id = uuid.uuid4().hex
        session_data = json.dumps(user.get_info())
        redis.redis_set(settings.REDIS_LOGIN, session_id, session_data)
        response = JsonResponse(response)
        response.set_cookie("session_id", session_id)
        return response
    except Exception as e:
        Log().error(e.__str__())


def userinfo_get(request):
    """
    获取用户信息接口，只需检查登录状态
    :param request:
    :return:
    """
    try:
        session_id = request.COOKIES.get('session_id')
        user_info = redis.redis_get(settings.REDIS_LOGIN, session_id)
        if user_info is None:
            response = {
                "code": 1,
                "message": "用户未登录",
            }
            return JsonResponse(response)
        else:
            user_info = json.loads(user_info)
        user_info.pop("id")
        user_info.update({"uname": user_info.pop("username")})
        response = {
            "code": 0,
            "message": "success",
            "data": user_info,
        }
        return JsonResponse(response)
    except Exception as e:
        Log().error(e.__str__())


def email_send(request):
    """
    发送邮箱验证码，检查request中是否携带session，没有需要创建session
    :param request:
    :return:
    """
    try:
        session_id = request.COOKIES.get('session_id')
        if session_id is None:
            session_id = uuid.uuid4().hex
        email = request.GET.get('email')
        if email is None:
            ret = {
                "code": 1,
                "message": "请输入邮箱"
            }
            return JsonResponse(ret)
        else:
            rabbit_mq(json.dumps({
                "email": email,
                "session_id": session_id,
            }))
            ret = {
                "code": 0,
                "message": "验证码发送成功",
            }
            response = JsonResponse(ret)
            response.set_cookie("session_id", session_id)
            return response
    except Exception as e:
        Log().error(e.__str__())


@wrapper_verify_check
def email_check(request):
    """
    检验邮箱验证码有效性,失败情况已在wrapper中处理
    :param request:
    :return:
    """
    try:
        session_id = request.COOKIES.get('session_id')
        data = json.loads(request.body)
        email = data.get('email')
        users = User.objects.filter(email=email)
        if len(users) == 0:
            ret = {
                "code": 2,
                "message": "邮箱不存在",
            }
            return JsonResponse(ret)
        user = users[0]
        ret = {
            "code": 0,
            "message": "success",
        }
        redis.redis_set(settings.REDIS_LOGIN, session_id, json.dumps(user.get_info()))
        return JsonResponse(ret)
    except Exception as e:
        Log().error(e.__str__())


def username_change(request):
    """
    修改用户名，需检查登录状态以及同步redis与数据库
    :param request:
    :return:
    """
    try:
        uid = request.uid
        session_id = request.COOKIES.get('session_id')
        data = json.loads(request.body)
        new_username = data.get('uname')
        # 检查重名
        if User.objects.filter(username=new_username):
            response = {
                "code": 2,
                "message": "用户名已存在",
            }
            return JsonResponse(response)
        else:
            users = User.objects.filter(id=uid)
            if len(users) == 0:
                response = {
                    "code": 1,
                    "message": "用户未登录",
                }
                return JsonResponse(response)
            user = users[0]
            user.username = new_username
            user.save()
            response = {
                "code": 0,
                "message": "用户名修改成功",
            }
            redis.redis_update_value(settings.REDIS_LOGIN, session_id, json.dumps(user.get_info()))
            return JsonResponse(response)
    except Exception as e:
        Log().error(e.__str__())


def password_change(request):
    """
    修改用户密码，需检查登录状态以及同步数据库
    :param request:
    :return:
    """
    try:
        uid = request.uid
        data = json.loads(request.body)
        new_password = decrypt(data.get('password'))

        users = User.objects.filter(id=uid)
        if len(users) == 0:
            response = {
                "code": 1,
                "message": "用户未登录",
            }
            return JsonResponse(response)
        user = users[0]
        user.set_password(new_password)
        user.save()
        response = {
            "code": 0,
            "message": "success",
        }
        return JsonResponse(response)
    except Exception as e:
        Log().error(e.__str__())


@wrapper_verify_check
def email_change(request):
    """
    修改邮箱，需要确认验证码，需要同步redis与数据库
    :param request:
    :return:
    """
    try:
        session_id = request.COOKIES.get('session_id')
        data = json.loads(request.body)
        new_email = data.get('email')
        if User.objects.filter(email=new_email):
            response = {
                "code": 3,
                "message": "邮箱已存在",
            }
            return JsonResponse(response)
        else:
            user_info = redis.redis_get(settings.REDIS_LOGIN, session_id)
            if user_info is None:
                response = {
                    "code": 1,
                    "message": "用户未登录",
                }
                return JsonResponse(response)
            else:
                user_info = json.loads(user_info)
            users = User.objects.filter(id=user_info.get("id"))
            if len(users) == 0:
                response = {
                    "code": 1,
                    "message": "用户未登录",
                }
                return JsonResponse(response)
            user = users[0]
            user.email = new_email
            user.save()
            response = {
                "code": 0,
                "message": "邮箱修改成功",
            }
            redis.redis_update_value(settings.REDIS_LOGIN, session_id, json.dumps(user.get_info()))
            return JsonResponse(response)
    except Exception as e:
        Log().error(e.__str__())


def avatar_change(request):
    """
    修改头像，需要确认验证码，需要同步redis与数据库
    :param uid: 用户id
    :param request:
    :return:
    """
    try:
        uid = request.uid
        session_id = request.COOKIES.get('session_id')
        data = json.loads(request.body)
        new_avatar = data.get('avatar')
        users = User.objects.filter(id=uid)
        if len(users) == 0:
            response = {
                "code": 1,
                "message": "用户未登录",
            }
            return JsonResponse(response)
        user = users[0]
        user.avatar = new_avatar
        user.save()
        response = {
            "code": 0,
            "message": "头像修改成功",
        }
        redis.redis_update_value(settings.REDIS_LOGIN, session_id, json.dumps(user.get_info()))
        return JsonResponse(response)
    except Exception as e:
        Log().error(e.__str__())
