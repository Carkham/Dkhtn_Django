import json
import uuid

from django.http import JsonResponse

from dkhtn_django.utils import redis_utils
from django.conf import settings

from dkhtn_django.utils.json_req_parser import JsonReq


def ret_code_check(response):
    """
    检查view层是否成功执行，目前接口成功执行code会设置为0
    :param response:
    :return: True or False
    """
    try:
        return json.loads(response.content.decode('utf-8'))['code'] == 0
    except Exception as e:
        e.__str__()
        return False


def redis_session_set(response, data, timeout):
    """
    设置全新的session id并更新response中的cookie
    :param response:
    :param data:
    :param timeout:
    :return: session_id
    """
    session_id = uuid.uuid4().hex
    redis_utils.redis_set(settings.REDIS_DB_LOGIN, session_id, data, timeout)
    response.set_cookie(settings.REDIS_SESSION_NAME, session_id)
    return session_id


def redis_login_update(request, response):
    """
    旧的session id丢弃，建立新的session id映射：
    session id -> userinfo
    user id -> session id
    :param request:
    :param response:
    :return:
    """
    # 禁止多点登录
    old_session_id = redis_utils.redis_get(settings.REDIS_DB_LOGIN, request.userinfo['id'])
    if old_session_id is not None:
        redis_utils.redis_delete(settings.REDIS_DB_LOGIN, old_session_id)
    # redis更新映射
    new_session_id = redis_session_set(response, json.dumps(request.userinfo), settings.REDIS_TIMEOUT)
    redis_utils.redis_set(settings.REDIS_DB_LOGIN, request.userinfo['id'], new_session_id)


def redis_user_read(request):
    """
    从redis中根据session id读取用户信息
    :param request:
    :return:
    """
    try:
        userinfo = redis_utils.redis_get(settings.REDIS_DB_LOGIN, request.COOKIES[settings.REDIS_SESSION_NAME])
        if userinfo is None:
            response = {
                "code": 1,
                "message": "用户未登录",
            }
            return JsonResponse(response)
        request.userinfo = json.loads(userinfo)
        return None
    except Exception as e:
        e.__str__()
        response = {
            "code": 1,
            "message": "用户未登录",
        }
        return JsonResponse(response)


def redis_user_write(request):
    try:
        user_info_json = json.dumps(request.userinfo)
        redis_utils.redis_set(settings.REDIS_DB_LOGIN, request.COOKIES[settings.REDIS_SESSION_NAME], user_info_json)
    except Exception as e:
        e.__str__()
        pass


def verify_session_get(request):
    """
    将生成的验证码置入session中
    对于忘记密码与注册，用户为未登录状态下操作，没有session id
    对于修改密码与修改邮箱，用户为已登录状态下操作，拥有session id
    session id唯一，对于已有的不应修改，对于没有的应当设置新的
    :param request:
    :return:
    """
    session_id = request.COOKIES.get(settings.REDIS_SESSION_NAME)
    if session_id is None:
        session_id = uuid.uuid4().hex
    return session_id


def verify_code_check(request):
    """
    邮箱验证码检验
    :param request:
    :return:
    """
    verify_message = redis_utils.redis_get(settings.REDIS_DB_VERIFY,
                                           request.COOKIES[settings.REDIS_SESSION_NAME])
    if verify_message is not None:
        verify_message = json.loads(verify_message)
    _request = JsonReq(request)
    if verify_message is None or verify_message['sms_code'] != _request.POST.get('email_sms'):
        response = {
            "code": 1,
            "message": "邮箱验证码错误或已失效",
        }
        return JsonResponse(response)
    else:
        request.email = verify_message['email']
        return None


def verify_email_check(request):
    """
    邮箱验证码检验
    :param request:
    :return:
    """
    verify_message = redis_utils.redis_get(settings.REDIS_DB_VERIFY,
                                           request.COOKIES[settings.REDIS_SESSION_NAME])
    if verify_message is not None:
        verify_message = json.loads(verify_message)
    if verify_message is None:
        response = {
            "code": 1,
            "message": "邮箱验证码错误或已失效",
        }
        return JsonResponse(response)
    else:
        request.email = verify_message['email']
        return None


def verify_code_delete(request):
    """
    及时删除redis中的邮箱验证码
    :param request:
    :return:
    """
    redis_utils.redis_delete(settings.REDIS_DB_VERIFY, request.COOKIES[settings.REDIS_SESSION_NAME])


def wrapper_set_login(func):
    """
    login接口专用，设置为无条件登录，并且拒绝多点登录
    维持登陆状态的redis映射：session_id->{id, name, avatar, email}
    检测多点登录的redis映射：id->session_id
    :param func:
    :return:
    """
    def inner(request, *args, **kwargs):
        # 在调用view函数前执行
        pass
        # 调用view函数
        ret = func(request, *args, **kwargs)
        # 在调用view函数后执行
        if ret_code_check(ret):
            redis_login_update(request, ret)
        return ret

    return inner


def wrapper_verify_send(func):
    """
    发送验证码前获取一下session id
    如果有说明是已登录状态下获取验证码，需维持登陆状态不能更新session id
    否则应当给与新的session id，来保证身份可验证
    :param func:
    :return:
    """
    def inner(request, *args, **kwargs):
        # 在调用view函数前执行
        # 获取正确的session id
        session_id = verify_session_get(request)
        # 调用view函数
        ret = func(request, session_id, *args, **kwargs)
        # 在调用view函数后执行
        # 写入redis，完成登录，redis中删除使用过的验证码
        if ret_code_check(ret):
            ret.set_cookie(settings.REDIS_SESSION_NAME, session_id)
        return ret

    return inner


def wrapper_verify_check(func):
    """
    检验邮箱验证码是否正确
    :param func:
    :return:
    """
    def inner(request, *args, **kwargs):
        # 在调用view函数前执行
        # 验证邮件
        ret = verify_code_check(request)
        if ret is not None:
            return ret
        else:
            response = {
                "code": 0,
                "message": "success",
            }
            return JsonResponse(response)
        # 调用view函数
        # ret = func(request, *args, **kwargs)
        # 在调用view函数后执行
        # 写入redis，完成登录，redis中删除使用过的验证码
        # if ret_code_check(ret):
        #     ret.set_cookie(settings.REDIS_SESSION_NAME, session_id)
        # return ret

    return inner


def wrapper_register(func):
    """
    检查session id是否存在，检查验证码
    调用register，进行注册
    设置redis，自动登录
    :param func:
    :return:
    """
    def inner(request, *args, **kwargs):
        # 在调用view函数前执行
        # 验证邮件
        ret = verify_code_check(request)
        if ret is not None:
            return ret
        # 调用view函数
        ret = func(request, *args, **kwargs)
        # 在调用view函数后执行
        # 写入redis，完成登录，redis中删除使用过的验证码
        if ret_code_check(ret):
            verify_code_delete(request)
            redis_login_update(request, ret)
        return ret

    return inner


def wrapper_userinfo_read(func):
    """
    只检查登陆状态，不含修改
    :param func:
    :return:
    """
    def inner(request, *args, **kwargs):
        # 在调用view函数前执行
        ret = redis_user_read(request)
        if ret is not None:
            return ret
        # 调用view函数
        ret = func(request, *args, **kwargs)
        # 在调用view函数后执行
        pass
        return ret

    return inner


def wrapper_modify(func):
    """
    登录验证+修改保存到redis
    :param func:
    :return:
    """
    def inner(request, *args, **kwargs):
        # 在调用view函数前执行
        ret = redis_user_read(request)
        if ret is not None:
            return ret
        # 调用view函数
        ret = func(request, *args, **kwargs)
        # 在调用view函数后执行
        if ret_code_check(ret):
            redis_user_write(request)
        return ret

    return inner


def wrapper_email_change(func):
    """
    检查登录
    检查验证码
    设置redis
    :param func:
    :return:
    """
    def inner(request, *args, **kwargs):
        # 在调用view函数前执行
        # 检验登录
        ret = redis_user_read(request)
        if ret is not None:
            return ret
        # 验证邮件
        ret = verify_code_check(request)
        if ret is not None:
            return ret
        # 调用view函数
        ret = func(request, *args, **kwargs)
        # 在调用view函数后执行
        if ret_code_check(ret):
            verify_code_delete(request)
            redis_user_write(request)
        return ret

    return inner


def wrapper_password_change(func):
    """
    检验邮箱验证码是否正确
    :param func:
    :return:
    """
    def inner(request, *args, **kwargs):
        # 在调用view函数前执行
        # 验证邮件
        ret = verify_email_check(request)
        if ret is not None:
            return ret
        # 调用view函数
        ret = func(request, *args, **kwargs)
        # 在调用view函数后执行
        if ret_code_check(ret):
            redis_user_write(request)
        return ret

    return inner
