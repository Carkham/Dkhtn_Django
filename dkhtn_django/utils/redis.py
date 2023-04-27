from django_redis import get_redis_connection
from django.conf import settings

redis_clis = {
    'default': get_redis_connection('default'),
    '1': get_redis_connection('1'),
}


def redis_get(index, key):
    """
    读redis
    :param index: redis库名称
    :param key: session_id
    :return:
    """
    if key is None:
        return None
    res = redis_clis[index].get(key)
    if res is not None:
        res = res.decode('utf-8')
    return res


def redis_set(index, key, value, timeout=settings.REDIS_TIMEOUT):
    """
    写redis
    :param index: redis库名称
    :param key: session_id
    :param value: session_data
    :param timeout: 失效时间，默认7天
    :return:
    """
    redis_clis[index].set(key, value, timeout)


def redis_delete(index, key):
    """
    删redis项
    :param index: redis库名称
    :param key: session_id
    :return:
    """
    redis_clis[index].delete(key)


def redis_update_key(index, old_key, new_key, timeout=settings.REDIS_TIMEOUT):
    """
    更新redis项,需保证old_key存在
    :param index: redis库名称
    :param old_key: 需要更新的session_id
    :param new_key: 新的session_id
    :param timeout: 失效时间，默认7天
    :return:
    """
    value = redis_get(index, old_key)
    redis_set(index, new_key, value, timeout)


def redis_update_value(index, key, value, timeout=settings.REDIS_TIMEOUT):
    """
    更新redis项,需保证key存在
    :param index: redis库名称
    :param key: session_id
    :param value: 新的session_data
    :param timeout: 失效时间，默认7天
    :return:
    """
    redis_set(index, key, value, timeout)
