# 实现优先级队列
import pickle
import time

from redis_queue.base import Queue


class PriorityRedisQueue(Queue):

    def get_nowait(self):
        """
        -1 -1: 默认获取优先级最大的数据
        0, 0 默认获取优先级最小的数据
        """
        # 先获取到这个数据
        # 然后将这个数据删除
        # 这两步应该是具有原子性的被完成
        ret = self.redis.zrange(self.name, -1, -1)
        self.redis.zrem(self.name, ret[0])
        if ret is None:
            raise self.Empty
        return pickle.loads(ret[0])
        # return ret[0]

    def put_nowait(self, obj):
        """
        向优先级队列中添加数据
        :param obj: 一个元组 (score, value)
        :return:
        """
        if self.lazy_limit and self.last_qsize < self.maxsize:
            pass
        elif self.full():
            raise self.Full
        self.last_qsize = self.redis.zadd(self.name, {pickle.dumps(obj[1]): obj[0]})
        # self.last_qsize = self.redis.zadd(self.name, {obj[1]: obj[0]})
        return True


q = PriorityRedisQueue(name="test_queue2", host="192.168.0.101")
datas = [(99, "kailun"), (100, "ruiyang"), (101, "rm")]
for data in datas:
    q.put(data)

print(q.get())
print(q.get())
print(q.get())
