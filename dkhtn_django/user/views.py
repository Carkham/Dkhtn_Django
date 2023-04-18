# from django.contrib.auth.models import User
import json

from django.http import JsonResponse
from django.conf import settings
from django.contrib import auth
from ..utils.json_req_parser import JsonReq
from .rabbit.RabbitMQ import rabbit_mq
from .models import User
from .wrappers import wrapper_set_login


def email_send(request):
    email = request.GET.get('email')
    if email is None:
        ret = {
            "code": 1,
            "message": "请输入邮箱"
        }
        return JsonResponse(ret)
    else:
        rabbit_mq(email)
        ret = {
            "code": 0,
            "message": "验证码发送成功",
        }
        return JsonResponse(ret)


def email_check(request):
    pass


# 获取RSA公钥
def rsa_get(request):
    response = {
        "code": 0,
        "message": "success",
        "data": settings.RSA_PUBLIC_KEY,
    }
    return JsonResponse(response)


# 登录接口，暂时不允许多点登录，多点登录涉及同步问题
@wrapper_set_login
def login(request):
    try:
        _request = JsonReq(request.body)
        username = _request.POST.get('uname')
        password = _request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        # 登录信息登记
        request.userinfo = user.userinfo()
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
            return JsonResponse(response)
    except Exception as e:
        raise e
        # response = {
        #     "code": 114514,
        #     "message": e.__str__(),
        # }
        # return JsonResponse(response)
