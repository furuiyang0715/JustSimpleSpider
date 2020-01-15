import redis
from redis import StrictRedis

from national_statistics.configs import REDIS_HOST, REDIS_PORT, REDIS_DATABASE_NAME
redis_cli = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DATABASE_NAME)


class SimpleHash(object):
    def __init__(self, cap, seed):
        self.cap = cap
        self.seed = seed

    def hash(self, value):
        ret = 0
        for i in range(value.__len__()):
            ret += self.seed * ret + ord(value[i])
        return (self.cap - 1) & ret


class RedisBloomFilter(object):
    def __init__(self, redis_client: StrictRedis, key: str):
        # 在创建的时候已经确定了容量以及错误率
        self.bit_size = 1 << 25
        self.seeds = [5, 7, 11, 13, 31, 37, 61]
        self.redis = redis_client
        self.hash_dict = []
        for i in range(self.seeds.__len__()):
            self.hash_dict.append(SimpleHash(self.bit_size, self.seeds[i]))
        self.key = key

    def is_contains(self, value):
        if value is None:
            return False
        if value.__len__() == 0:
            return False
        ret = True
        for f in self.hash_dict:
            loc = f.hash(value)
            ret = ret & self.redis.getbit(self.key, loc)
        return ret

    def insert(self, value):
        for f in self.hash_dict:
            loc = f.hash(value)
            self.redis.setbit(self.key, loc, 1)

    def restart(self):
        self.redis.delete(self.key)


# class BloomFilterAdapter(object):
#     # 针对布隆过滤器的扩展 用一个新的布隆过滤器和多个老的布隆过滤器共同组成一个新的过滤器，提供相同的接口。
#     def __init__(self, old_filters, new_filter):
#         self.old_filters = old_filters
#         self.new_filter = new_filter
#
#     def add(self, key):
#         self.new_filter.add(key)
#
#     def exists(self, key):
#         # 依次检查是否在每一个中出现过
#         return any([f.exists(key) for f in self.old_filters]) or self.new_filter.exists(key)
#
#     def __len__(self):
#         # 当前的唯一总数
#         return sum([len(f) for f in self.old_filters]) + len(self.new_filter)


# https://juejin.im/post/5cfb9c74e51d455d6d5357db
# https://blog.csdn.net/KWSY2008/article/details/48290299

# if __name__ == "__main__":
#     bloom = RedisBloomFilter(redis_cli, "test_key")
#     bloom.insert("ruiyang")
#     r = bloom.is_contains("ruiyang")  # 1
#     r1 = bloom.is_contains("kailun")  # 0
#     print(r, r1)
