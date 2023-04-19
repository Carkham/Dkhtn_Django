import json

from django.conf import settings
from django.contrib import auth
from django.http import JsonResponse

from ..utils.json_req_parser import JsonReq
from .rabbit.RabbitMQ import rabbit_mq
from .wrappers import wrapper_set_login, wrapper_verify_send, wrapper_verify_check, wrapper_register
from .models import User


@wrapper_verify_send
def email_send(request, session_id):
    _request = JsonReq(request)
    email = _request.GET.get('email')
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
        return JsonResponse(ret)


@wrapper_verify_check
def email_check(request):
    """
        功能在装饰器中已经完成
        :param request:
        :return:
        """
    pass


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


@wrapper_set_login
def login(request):
    """
    登录接口，暂时不允许多点登录，多点登录涉及同步问题
    :param request:
    :return: JsonResponse
    """
    try:
        _request = JsonReq(request)
        username = _request.POST.get('uname')
        password = _request.POST.get('password')
        user = auth.authenticate(username=username, password=password)
        if user is None:
            response = {
                "code": 1,
                "message": "用户名或邮箱号或密码错误",
            }
            return JsonResponse(response)
        else:
            # 登录信息登记
            if isinstance(user, User):
                request.userinfo = user.userinfo()
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


@wrapper_register
def register(request):
    """
    注册，流程为->（前端）先调用获取邮箱验证码接口->（后端）发送验证邮件，建立session id，存储验证码，
    反馈前端->（前端）调用用户注册接口->（后端）检验session id，检验验证码，注册成功则直接登录
    :param request:
    :return:
    """
    try:
        _request = JsonReq(request)
        username = _request.POST.get('uname')
        password = _request.POST.get('password')
        email = _request.POST.get('email')
        avatar = _request.POST.get('avatar')
        # 检查重名
        old_user = User.objects.filter(username=username)
        if old_user:
            response = {
                "code": 2,
                "message": "用户名已存在",
            }
            return JsonResponse(response)
        # 检查邮箱重复
        old_user = User.objects.filter(email=email)
        if old_user:
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
        request.userinfo = user.userinfo()
        response = {
            "code": 0,
            "message": "注册成功",
        }
        return JsonResponse(response)
    except Exception as e:
        raise e
        # response = {
        #     "code": 114514,
        #     "message": e.__str__(),
        # }
        # return JsonResponse(response)
