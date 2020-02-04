#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Binux<roy@binux.me>
#         http://binux.me
# Created on 2015-04-27 22:48:04

import time
import redis
# 进行序列化的一个工具 在此对其进行改写 使用 pickle 完成相应的工作
# import umsgpack
import pickle
from six.moves import queue as BaseQueue


class RedisQueue(object):
    """
    A Queue like message built over redis
    """

    Empty = BaseQueue.Empty
    Full = BaseQueue.Full
    max_timeout = 0.3

    def __init__(self, name, host='localhost', port=6379, db=0,
                 maxsize=0, lazy_limit=True, password=None, cluster_nodes=None):
        """
        Constructor for RedisQueue
        maxsize:    an integer that sets the upperbound limit on the number of
                    items that can be placed in the queue.
        lazy_limit: redis queue is shared via instance, a lazy size limit is used
                    for better performance.
        """
        self.name = name
        if(cluster_nodes is not None):
            # 使用的是 redis 集群
            from rediscluster import StrictRedisCluster
            self.redis = StrictRedisCluster(startup_nodes=cluster_nodes)
        else:
            self.redis = redis.StrictRedis(host=host, port=port, db=db, password=password)
        self.maxsize = maxsize
        self.lazy_limit = lazy_limit
        self.last_qsize = 0

    def qsize(self):
        """
        求出队列的长度
        :return:
        """
        self.last_qsize = self.redis.llen(self.name)
        return self.last_qsize

    def empty(self):
        """
        判断队列是否为空
        :return:
        """
        if self.qsize() == 0:
            return True
        else:
            return False

    def full(self):
        """
        判断队列是否已满
        :return:
        """
        if self.maxsize and self.qsize() >= self.maxsize:
            return True
        else:
            return False

    def put_nowait(self, obj):
        """
        无阻塞地向队列中添加数据
        无阻塞的意思是如果队列已满 就立即抛出异常
        :param obj:
        :return:
        """
        if self.lazy_limit and self.last_qsize < self.maxsize:
            pass
        elif self.full():
            raise self.Full
        # 从左边进 从右边出 默认是一个先进先出的队列
        # self.last_qsize = self.redis.rpush(self.name, umsgpack.packb(obj))
        self.last_qsize = self.redis.rpush(self.name, pickle.dumps(obj))
        return True

    def put(self, obj, block=True, timeout=None):
        """
        阻塞式地向队列中添加数据
        阻塞的意思是 如果队列已满 就等待
        :param obj:
        :param block:  是否阻塞
        :param timeout:  最大的等待时间
        :return:
        """
        if not block:
            return self.put_nowait(obj)

        start_time = time.time()
        while True:
            try:
                return self.put_nowait(obj)
            except self.Full:
                if timeout:
                    lasted = time.time() - start_time
                    if timeout > lasted:
                        time.sleep(min(self.max_timeout, timeout - lasted))
                    else:
                        raise
                else:
                    time.sleep(self.max_timeout)

    def get_nowait(self):
        """
        无延迟地从队列中获取数据
        :return:
        """
        # 左进右出 默认是一个先进先出的队列
        ret = self.redis.lpop(self.name)
        if ret is None:
            raise self.Empty
        # return umsgpack.unpackb(ret)
        return pickle.loads(ret)

    def get(self, block=True, timeout=None):
        """
        阻塞地从对列中获取
        :param block:
        :param timeout:
        :return:
        """
        if not block:
            return self.get_nowait()

        start_time = time.time()
        while True:
            try:
                return self.get_nowait()
            except self.Empty:
                if timeout:
                    lasted = time.time() - start_time
                    if timeout > lasted:
                        time.sleep(min(self.max_timeout, timeout - lasted))
                    else:
                        raise
                else:
                    time.sleep(self.max_timeout)

Queue = RedisQueue


if __name__ == "__main__":
    q = Queue(name="test_queue", host="192.168.0.101")
    for i in range(100):
        q.put(i)

    for j in range(100):
        print(q.get())
