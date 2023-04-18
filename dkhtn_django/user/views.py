from django.conf import settings
from django.contrib import auth
from django.http import JsonResponse

from ..utils.json_req_parser import JsonReq
from .rabbit.RabbitMQ import rabbit_mq
from .wrappers import wrapper_set_login
from .models import User


def email_send(request):
    _request = JsonReq(request)
    email = _request.GET.get('email')
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
