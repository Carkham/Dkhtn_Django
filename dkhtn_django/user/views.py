# from django.contrib.auth.models import User
from django.http import JsonResponse
from .rabbit.RabbitMQ import rabbit_mq
from django.conf import settings


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
