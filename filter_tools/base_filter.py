# 基于信摘要算法进行去重判断以及存储

# 1. 基于内存的存储
# 2. 基于redis的存储
# 3. 基于mysql的存储

import six
import hashlib


class BaseFilter(object):
    """基于信息摘要算法进行数据的去重以及判断"""
    def __init__(self, hash_func_name='md5',
                 redis_host='localhost',
                 redis_port=6379,
                 redis_db=15,
                 redis_key='filter',
                 mysql_url=None,
                 mysql_table_name='filter'
                 ):
        self.hash_func = getattr(hashlib, hash_func_name)
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_db = redis_db
        self.redis_key = redis_key
        self.mysql_url = mysql_url
        self.mysql_table_name = mysql_table_name
        self.storage = self._get_storage()

    def _get_storage(self):
        """
        获取去重容器对象
        在具体的子类中实现
        :return:
        """
        pass

    def _safe_date(self, data):
        """
        python2 str --> python3 bytes
        python2 unicode --> python3 str
        :param data: 给定的原始数据
        :return: 二进制类型的字符串数据
        """
        if six.PY3:
            if isinstance(data, bytes):
                return data
            elif isinstance(data, str):
                return data.encode()
            else:
                raise Exception("请提供字符串数据")
        # elif six.PY2:
        #     if isinstance(data, str):
        #         return data
        #     elif isinstance(data, unicode):
        #         return data.encode()
        #     else:
        #         raise Exception("请提供字符串数据")

    def _get_hash_value(self, data):
        """
        根据给定的数据 返回对应的 hash 摘要信息
        :param data:
        :return:
        """
        # 创建一个 hash 对象
        hash_obj = self.hash_func()
        hash_obj.update(self._safe_date(data))
        hash_value = hash_obj.hexdigest()
        return hash_value

    def save(self, data):
        """
        根据 data 计算出对应的指纹进行存储
        :param data:
        :return:
        """
        hash_value = self._get_hash_value(data)
        return self._save(hash_value)

    def _save(self, hash_value):
        """
        交给对应的子类去具体实现
        :param hash_value:
        :return:
        """
    def is_exist(self, data):
        """
        判断给定的数据是否存在
        :param data:
        :return:
        """
        hash_value = self._get_hash_value(data)
        return self._is_exist(hash_value)

    def _is_exist(self, hash_value):
        """
        交给对应的子类去实现
        判断的结果是 True 或者是 False
        :param hash_value:
        :return:
        """
