import json
import uuid

from dkhtn_django.utils import redis_utils
from django.conf import settings


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
