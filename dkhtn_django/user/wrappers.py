import json
import uuid

from dkhtn_django.utils import redis_utils
from django.conf import settings


# 检查view层是否成功执行，目前接口成功执行code会设置为0
def ret_code_check(ret):
    try:
        return json.loads(ret.content.decode('utf-8'))['code'] == 0
    except:
        return False


# 设置全新的session id并更新response中的cookie
def redis_session_set(ret, data, timeout):
    session_id = uuid.uuid4().hex
    redis_utils.redis_set(settings.REDIS_DB_LOGIN, session_id, data, timeout)
    ret.set_cookie(settings.REDIS_SESSION_NAME, session_id)
    return session_id


# 旧的session id丢弃，建立新的session id映射：
# session id -> userinfo
# user id -> session id
def redis_login_update(request, ret):
    # 禁止多点登录
    old_session_id = redis_utils.redis_get(settings.REDIS_DB_LOGIN, request.userinfo['id'])
    if old_session_id is not None:
        redis_utils.redis_delete(settings.REDIS_DB_LOGIN, old_session_id)
    # redis更新映射
    new_session_id = redis_session_set(ret, json.dumps(request.userinfo), settings.REDIS_TIMEOUT)
    redis_utils.redis_set(settings.REDIS_DB_LOGIN, request.userinfo['id'], new_session_id)


# login接口专用，设置为无条件登录，并且拒绝多点登录
# 维持登陆状态的redis映射：session_id->{id, name, avatar, email}
# 检测多点登录的redis映射：id->session_id
def wrapper_set_login(func):
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
