import json

from django.conf import settings
from django.contrib import auth
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse

from ..utils.json_req_parser import JsonReq
from .rabbit.RabbitMQ import rabbit_mq
from .wrappers import wrapper_set_login, wrapper_verify_send, wrapper_verify_check, wrapper_register, \
    wrapper_userinfo_read, wrapper_modify, wrapper_email_change
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


@wrapper_userinfo_read
def userinfo_get(request):
    """
    获取用户信息接口，只需检查登录状态
    :param request:
    :return:
    """
    try:
        data = {
            "uname": request.userinfo['username'],
            "avatar": request.userinfo['avatar'],
            "email": request.userinfo['email'],
        }
        response = {
            "code": 0,
            "message": "success",
            "data": data,
        }
        return JsonResponse(response)
    except Exception as e:
        raise e
        # response = {
        #     "code": 114514,
        #     "message": e.__str__(),
        # }
        # return JsonResponse(response)


@wrapper_modify
def username_change(request):
    """
    修改用户名，需检查登录状态以及同步redis与数据库
    :param request:
    :return:
    """
    try:
        _request = JsonReq(request)
        new_username = _request.POST.get('uname')
        user_repeat = User.objects.filter(username=new_username)
        # 检查重名
        if user_repeat:
            response = {
                "code": 2,
                "message": "用户名已存在",
            }
            return JsonResponse(response)
        else:
            # 修改用户名，用户id唯一所以结果一定唯一
            # 大离谱事件，如果user = User.objects.filter(id=request.userinfo['id'])
            # 然后user[0].username = new_username，会发现user[0]修改失败，然鹅下面这样写不会失败
            users = User.objects.filter(id=request.userinfo['id'])
            if len(users) <= 0:
                response = {
                    "code": 3,
                    "message": "用户不存在",
                }
                return JsonResponse(response)
            user = users[0]
            user.username = new_username
            # 修改信息登记
            request.userinfo['username'] = new_username
            # 同步到数据库
            user.save()
            response = {
                "code": 0,
                "message": "用户名修改成功",
            }
            return JsonResponse(response)
    except Exception as e:
        raise e
        # response = {
        #     "code": 114514,
        #     "message": e.__str__(),
        # }
        # return JsonResponse(response)


@wrapper_modify
def password_change(request):
    """
    修改用户密码，需检查登录状态以及同步数据库，其实可以不要modify用login check装饰器
    :param request:
    :return:
    """
    try:
        _request = JsonReq(request)
        new_password = make_password(_request.POST.get('password'))

        users = User.objects.filter(id=request.userinfo['id'])
        if len(users) <= 0:
            response = {
                "code": 2,
                "message": "用户不存在",
            }
            return JsonResponse(response)
        user = users[0]

        user.password = new_password
        # 同步到数据库
        user.save()
        response = {
            "code": 0,
            "message": "success",
        }
        return JsonResponse(response)
    except Exception as e:
        raise e
        # response = {
        #     "code": 114514,
        #     "message": e.__str__(),
        # }
        # return JsonResponse(response)


@wrapper_email_change
def email_change(request):
    """
    修改邮箱，需要确认验证码，需要同步redis与数据库
    :param request:
    :return:
    """
    try:
        _request = JsonReq(request)
        new_email = _request.POST.get('email')
        user_repeat = User.objects.filter(email=new_email)
        # 检查重复邮箱
        if user_repeat:
            response = {
                "code": 3,
                "message": "邮箱已存在",
            }
            return JsonResponse(response)
        else:
            # 修改邮箱
            users = User.objects.filter(id=request.userinfo['id'])

            for i in range(300):
                fuck = User.objects.filter(id=i)
                if len(fuck) > 0:
                    print("cnm " + str(i))

            if len(users) <= 0:
                response = {
                    "code": 4,
                    "message": "用户不存在",
                }
                return JsonResponse(response)
            user = users[0]

            user.email = new_email
            # 修改信息登记
            request.userinfo['email'] = new_email
            # 同步到数据库
            user.save()
            response = {
                "code": 0,
                "message": "邮箱修改成功",
            }
            return JsonResponse(response)
    except Exception as e:
        raise e
        # response = {
        #     "code": 114514,
        #     "message": e.__str__(),
        # }
        # return JsonResponse(response)
