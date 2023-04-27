import json

from django.http import JsonResponse
from django.conf import settings

from dkhtn_django.utils import redis


def wrapper_verify_check(func):
    """
    检验邮箱验证码是否正确
    :param func:
    :return:
    """

    def inner(request):
        # 验证邮件
        email_verify = redis.redis_get(settings.REDIS_VERIFY, request.COOKIES.get("session_id"))
        if email_verify is None:
            response = {
                "code": 1,
                "message": "邮箱验证码错误或已失效",
            }
            return JsonResponse(response)
        else:
            email_verify = json.loads(email_verify)
        data = json.loads(request.body)
        if data.get("email") != email_verify.get("email") or data.get("email_sms") != email_verify.get("email_sms"):
            response = {
                "code": 1,
                "message": "邮箱验证码错误或已失效1",
            }
            return JsonResponse(response)
        redis.redis_delete(settings.REDIS_VERIFY, request.COOKIES.get("session_id"))
        return func(request)

    return inner
