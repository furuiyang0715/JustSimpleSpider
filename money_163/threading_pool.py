#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# 文件名：thread_pool.py
import random
import time
from threading import Thread
from queue import Queue
import requests

from money_163.configs import MYSQL_HOST, MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB
from money_163.my_log import logger
from money_163.sql_base import StoreTool


class MyThread(Thread, StoreTool):
    """自定义线程对象"""
    def __init__(self, *args, **kwargs):
        conf = {
            "host": MYSQL_HOST,
            "port": MYSQL_PORT,
            "user": MYSQL_USER,
            "password": MYSQL_PASSWORD,
            "db": MYSQL_DB,
        }
        StoreTool.__init__(self, **conf)

        Thread.__init__(self, *args, **kwargs)
        self.datas = None

    def run(self):
        url = self.datas.get("l")
        # 判断数据库中是否存在该 url

        ret = requests.get(url)
        if ret.status_code == 200:
            print("请求 {} 成功".format(url))
            self.datas.update({"article": "我是文章 " + str(time.time())})
            if self._is_exist(url):
                logger.warning("数据{}已存在".format(url))
            else:
                self.save(self.datas)
                logger.info("数据{}保存成功".format(url))

        self.close()


class BaseSpider(object):
    def __init__(self):
        # 队列
        self.queue = Queue()
        # 线程池
        self.threads_pool = []
        # 正在运行的线程数量
        self.running_thread = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
        }

    def init_thread(self, count):
        """
        初始化线程池
        :param count: 线程池中要保留的线程的个数
        :return:
        """
        thread_count = len(self.threads_pool)
        for i in range(thread_count, count):
            thead = MyThread()
            thead.setName('第' + str(i) + '号线程')
            self.threads_pool.append(thead)

    def put(self, item):
        self.queue.put(item)

    def get(self):
        ret = None
        try:
            ret = self.queue.get(block=False)
        except:
            pass
        return ret

    # 获取可用线程 - 优化思路： 每次都遍历一遍效率低，可以封装对象，设置标示位，执行结束后改变标志位状态；
    # 但这样还是要循环一遍；此时取到一定数量或者快到头了，然后再从头遍历
    def get_available(self):
        """
        从线程池中获取一个可用的空闲线程
        :return:
        """
        for c_thread in self.threads_pool:
            if not c_thread.isAlive():
                self.threads_pool.remove(c_thread)
                return c_thread
        # 扩容线程
        self.init_thread(16)
        return self.get_available()


def test2():
    now = lambda: time.time()
    t1 = now()
    url_list = [
                   'http://www.baidu.com',
                   'https://github.com/FanChael/DocPro',
                   'http://www.baidu.com',
                   'http://www.baidu.com',
                   'http://www.baidu.com',
                   'https://github.com/FanChael/DocPro',
                   'http://www.baidu.com',
                   'http://www.baidu.com',
                   'http://www.baidu.com',
                   'http://www.baidu.com',
                   'http://www.baidu.com',
                   'https://github.com/FanChael',
                   'https://github.com/FanChael',
               ] * 2
    for u in url_list:
        ret = requests.get(u)
        if ret.status_code == 200:
            print("请求{}成功".format(u))
    print("用时{}".format(now() - t1))


def test1():
    now = lambda: time.time()
    t1 = now()
    url_list = [
        'http://www.baidu.com',
        'https://github.com/FanChael/DocPro',
        'http://www.baidu.com',
        'http://www.baidu.com',
        'http://www.baidu.com',
        'https://github.com/FanChael/DocPro',
        'http://www.baidu.com',
        'http://www.baidu.com',
        'http://www.baidu.com',
        'http://www.baidu.com',
        'http://www.baidu.com',
        'https://github.com/FanChael',
        'https://github.com/FanChael',
    ] * 2

    spider = BaseSpider()
    spider.init_thread(16)
    start_time = time.time()
    for url in url_list:
        spider.put({"url": url})

    print("将请求放入队列所用的时间是{}".format(now() - t1))

    while True:
        item = spider.get()
        if not item:
            break
        a_thread = spider.get_available()
        a_thread.datas = item
        if a_thread:
            spider.running_thread.append(a_thread)
            a_thread.start()

    for t in spider.running_thread:
        if t.isAlive():
            t.join()

    # 结束时间
    end_time = time.time()
    print(len(spider.running_thread), '个线程, ', '运行时间: ', end_time - start_time, '秒')
    print('空余线程数: ', len(spider.threads_pool))


# test1()