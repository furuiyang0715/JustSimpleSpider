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
        # client = redis.StrictRedis(host='localhost', port=6379, db=15)
        # return client

        # 增加 redis 连接对象的复用性
        pool = redis.ConnectionPool(host=self.redis_host,
                                    port=self.redis_port,
                                    db=self.redis_db)
        client = redis.StrictRedis(connection_pool=pool)
        return client

    def _save(self, hash_value):
        """
        利用 redis 的无序集合进行存储
        :param hash_value:
        :return:
        """
        return self.storage.sadd(self.redis_key, hash_value)

    def _is_exist(self, hash_value):
        """
        判断 redis 的无序集合中是否有对应的判断依据
        :param hash_value:
        :return:
        """
        if self.storage.sismember(self.redis_key, hash_value):
            return True
        else:
            return False


if __name__ == "__main__":
    f = RedisFilter()
    datas = ['ruiyang', 'Ruiyang', '33', 'pwd', "11", "22", "33", "ruiyang"]
    for d in datas:
        if f.is_exist(d):
            print("{} 数据已经存在".format(d))
            # print(f.storage)
        else:
            f.save(d)
            print("添加数据 {}".format(d))