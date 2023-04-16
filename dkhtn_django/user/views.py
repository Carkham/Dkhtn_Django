# from django.contrib.auth.models import User
from django.http import JsonResponse
from .rabbit.RabbitMQ import rabbit_mq


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
