# from django.contrib.auth.models import User
from django.http import JsonResponse
from .rabbit.RabbitMQ import RabbitMQ
from .rabbit.EmailSender import send_email
from django.conf import settings


def email_send(request):
    email = request.GET.get('email')
    #FIXME: 我靠要是没有'email'字段怎么办
    if settings.DEBUG:
        send_email(email)
    else:
        RabbitMQ(email)
    ret = {
        "code": 0,
        "message": "验证码发送成功",
    }
    return JsonResponse(ret)


def email_check(request):
    pass
