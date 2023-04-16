# from django.contrib.auth.models import User
from django.http import JsonResponse
from .rabbit.RabbitMQ import RabbitMQ


def email_send(request):
    email = request.GET.get('email')
    RabbitMQ(email)
    ret = {
        "code": 0,
        "message": "验证码发送成功",
    }
    return JsonResponse(ret)


def email_check(request):
    pass
