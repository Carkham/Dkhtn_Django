from django_redis import get_redis_connection
from django.conf import settings

redis_clis = {
    'default': get_redis_connection('default'),
    '1': get_redis_connection('1'),
}


def redis_get(db_index, key):
    """
    读redis
    :param db_index: redis库名称
    :param key:
    :return:
    """
    res = redis_clis[db_index].get(key)
    if res is not None:
        res = res.decode('utf-8')
    return res


def redis_set(db_index, key, value, timeout=settings.REDIS_TIMEOUT):
    """
    写redis
    :param db_index: redis库名称
    :param key:
    :param value:
    :param timeout:
    :return:
    """
    redis_clis[db_index].set(key, value, timeout)


def redis_delete(db_index, key):
    """
    删redis项
    :param db_index: redis库名称
    :param key:
    :return:
    """
    redis_clis[db_index].delete(key)
