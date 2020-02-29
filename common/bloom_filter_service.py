# 基于 redis 的布隆过滤器的实现

# （1） 多个 hash 函数的实现和求值
# （2） hash 表的实现以及实现对应的映射以及判断

import hashlib
import redis


def simple_hash(value):
    import hashlib

    if isinstance(value, str):
        value = value.encode()

    m5 = hashlib.md5()
    m5.update(value)
    hash_value = m5.hexdigest()
    return hash_value


class MultipleHash(object):
    def __init__(self, salts, hash_func_name='md5'):
        """
        该类实现对某个数值进行加盐hash的过程
        :param salts: 对原始的数据进行预定义加盐
        :param hash_func_name: 可使用多个 hash 函数
        """
        self.hash_func = getattr(hashlib, hash_func_name)
        if len(salts) < 3:
            raise Exception("请至少输入 3 个 salts")
        self.salts = salts

    def _safe_data(self, data):
        """
        对即将hash的数据进行预处理
        这里我已经确认我运行在 py3 环境中
        就不像之前一样对系统进行判断
        :param data:
        :return:
        """
        if isinstance(data, str):
            return data.encode()
        elif isinstance(data, bytes):
            return data
        else:
            raise Exception("被hash值必须是一个字符串")

    def get_hash_value(self, data):
        """
        根据提供的数据 返回多个hash函数值
        :param data:
        :return:
        """
        hash_values = []
        for i in self.salts:
            hash_obj = self.hash_func()
            hash_obj.update(self._safe_data(data))
            hash_obj.update(self._safe_data(i))
            ret = hash_obj.hexdigest()
            # 将结果的 16 进制字节转换为 10 进制
            hash_values.append(int(ret, 16))
        return hash_values


class BloomFilter(object):
    def __init__(self,
                 redis_host='localhost',
                 redis_port=6379,
                 redis_db=0,
                 redis_key="bloomfilter",
                 salts=('1', '2', '3'),
                 ):

        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_key = redis_key
        self.client = self.get_redis_client()
        self.multihash = MultipleHash(salts)

    def restart(self):
        self.client.delete(self.redis_key)

    def get_redis_client(self):
        """
        获取一个redis连接对象
        :return:
        """
        pool = redis.ConnectionPool(host=self.redis_host, port=self.redis_port, db=self.redis_db)
        client = redis.StrictRedis(connection_pool=pool)
        return client

    def _get_offset(self, hash_value):
        return hash_value % (512*1024*1024*8)  # 9 + 10 + 10 + 3 = 32

    def save(self, data):
        """
        将值存入布隆过滤器
        :param data:
        :return:
        """
        hash_values = self.multihash.get_hash_value(data)
        for hash_value in hash_values:
            offset = self._get_offset(hash_value)
            self.client.setbit(self.redis_key, offset, 1)
        return True

    def is_exist(self, data):
        """
        判断某个值在布隆过滤器中是否存在
        :param data:
        :return:
        """
        hash_values = self.multihash.get_hash_value(data)
        for hash_value in hash_values:
            offset = self._get_offset(hash_value)
            ret = self.client.getbit(self.redis_key, offset)
            if not ret:
                return False
        return True


class BloomFilterAdapter(object):
    '''
    针对布隆过滤器的扩展 用一个新的布隆过滤器和多个老的布隆过滤器共同组成一个新的过滤器，提供相同的接口。
    '''
    def __init__(self, old_filters, new_filter: BloomFilter):
        if not isinstance(old_filters, list):
            old_filters = [old_filters]

        self.old_filters = old_filters
        self.new_filter = new_filter

    def save(self, key):
        self.new_filter.save(key)

    def is_exist(self, key):
        return any([f.is_exist(key) for f in self.old_filters]) or self.new_filter.is_exist(key)

    def restart(self):
        for filter in self.old_filters:
            filter.restart()
        self.new_filter.restart()


def test_bloom():
    # h = MultipleHash(salts=['1', '2', '3'])
    bloom = BloomFilter(redis_host='127.0.0.1')
    bloom.restart()
    datas = list("talkischeapshowmethecode")
    for data in datas:
        if bloom.is_exist(data):
            print("{} 已经存在".format(data))
        else:
            bloom.save(data)
            print("{} 存储成功".format(data))


def test_adapter():
    bloom1 = BloomFilter(redis_host='127.0.0.1', redis_key='bloom1')
    bloom2 = BloomFilter(redis_host='127.0.0.1', redis_key='bloom2')
    bloom3 = BloomFilter(redis_host='127.0.0.1', redis_key='bloom3')
    bloom1.save("apple")
    bloom2.save("orange")
    bloom3.save("child")
    adap = BloomFilterAdapter([bloom1, bloom2], bloom3)
    print(adap.is_exist('apple'))
    print(adap.is_exist('orange'))
    print(adap.is_exist('child'))
    print(adap.is_exist('happy'))

    adap.save("happy")
    print(adap.is_exist('happy'))

    # adap.restart()


if __name__ == "__main__":
    test_bloom()

    # test_adapter()
