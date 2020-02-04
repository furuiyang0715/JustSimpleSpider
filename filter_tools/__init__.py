from filter_tools.bloom_filter import BloomFilter
from filter_tools.memory_filter import MemoryFilter
from filter_tools.mysql_filter import MqlFilter
from filter_tools.redis_filter import RedisFilter


def get_filter_class(cls_name):
    """
    返回对应的过滤器的类对象
    :param cls_name:
    :return:
    """
    if cls_name == "bloom":
        return BloomFilter
    elif cls_name == "memory":
        return MemoryFilter
    elif cls_name == "mysql":
        return MqlFilter
    elif cls_name == "redis":
        return RedisFilter
    else:
        raise Exception("该去重过滤器不存在")
