import redis

from filter_tools.base_filter import BaseFilter


class RedisFilter(BaseFilter):
    """
    基于redis的持久化存储的去重判断依据的实现
    """

    def _get_storage(self):
        """
        返回一个 redis 连接对象
        :return:
        """
        client = redis.StrictRedis(host='localhost', port=6379, db=15)
        return client

    def _save(self, hash_value):
        """
        利用 redis 的无序集合进行存储
        :param hash_value:
        :return:
        """

    def _is_exist(self, hash_value):
        """
        判断 redis 的无序集合中是否有对应的判断依据
        :param hash_value:
        :return:
        """
