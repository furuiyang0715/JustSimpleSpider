import random
import time

import pymysql
import threadpool

import sys
sys.path.append('./../../')

from PublicOpinion.carticle.cbase import CArticleBase
from PublicOpinion.configs import DC_HOST, DC_PORT, DC_USER, DC_PASSWD, DC_DB

now = lambda: time.time()


class Schedule(object):
    def __init__(self):
        self.keys = sorted(self.dc_info().values())
        random.shuffle(self.keys)

    def dc_info(self):  # {'300150.XSHE': '世纪瑞尔',
        """
        从 datacanter.const_secumain 数据库中获取当天需要爬取的股票信息
        返回的是 股票代码: 中文名简称 的字典的形式
        """
        try:
            conn = pymysql.connect(host=DC_HOST, port=DC_PORT, user=DC_USER,
                                   passwd=DC_PASSWD, db=DC_DB)
        except Exception as e:
            raise

        cur = conn.cursor()
        cur.execute("USE datacenter;")
        cur.execute("""select SecuCode, ChiNameAbbr from const_secumain where SecuCode \
            in (select distinct SecuCode from const_secumain);""")
        dc_info = {r[0]: r[1] for r in cur.fetchall()}
        cur.close()
        conn.close()
        return dc_info

    def start(self, key):
        c = CArticleBase(key=key)
        c.start()

    def thread_run(self):
        start_time = now()
        pool = threadpool.ThreadPool(4)
        requests = threadpool.makeRequests(self.start, self.keys)
        [pool.putRequest(req) for req in requests]
        pool.wait()
        print("用时: {}".format(now() - start_time))

    def simple_run(self):
        # 代理状态不好 所以不开启多线程了 一会就崩了
        start_time = now()
        for key in self.keys:
            self.start(key)
        print("用时: {}".format(now() - start_time))


sche = Schedule()
sche.simple_run()
