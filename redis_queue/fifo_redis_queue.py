# 先进先出的队列
from redis_queue.base import Queue


class FifoRedisQueue(Queue):
    """
    先进先出的队列 继承即可使用
    """
    pass


q = FifoRedisQueue(name="test_queue", host="192.168.0.101")
for i in range(100):
    q.put(i)

for j in range(100):
    print(q.get())