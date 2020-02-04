import pickle

from redis_queue.base import Queue


class LifoReidsQueue(Queue):
    """
    后进先出的队列
    需要重写 get_nowait 以及 put_nowait 方法
    """
    def get_nowait(self):
        """
        无延迟地从队列中获取数据
        :return:
        """
        # 默认是左进右出
        # 改为右进右出 即为一个后进先出的队列
        ret = self.redis.rpop(self.name)
        if ret is None:
            raise self.Empty
        return pickle.loads(ret)


q = LifoReidsQueue(name="test_queue", host="192.168.0.101")
for i in range(100):
    q.put(i)

for j in range(100):
    print(q.get())