import json

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

from django.conf import settings
from dkhtn_django.utils import redis
from dkhtn_django.utils.log import Log


class LoginCheck(MiddlewareMixin):

    def process_request(self, request):
        pass_path = ["/api/user/login", "/api/user/register", "/api/user/email-check", "/api/user/rsa-pub"]
        if request.path in pass_path:
            return None
        else:
            user_info = redis.redis_get(settings.REDIS_LOGIN, request.COOKIES.get("session_id"))
            if user_info is None:
                response = {
                    "code": -1,
                    "message": "用户未登录",
                }
                return JsonResponse(response)
            else:
                request.uid = json.loads(user_info).get("id")
                return None


    def process_exception(self, request, exception):
        Log().error(exception.__str__())
        response = {
            "code": -1,
            "message": "请求错误",
        }
        return JsonResponse(response)
