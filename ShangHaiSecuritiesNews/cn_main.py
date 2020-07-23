import os
import sys

import threadpool

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from ShangHaiSecuritiesNews.cn_4_hours import CN4Hours
from ShangHaiSecuritiesNews.cn_hongguan import CNStock


class CNSchedule(object):
    """上海证券报 爬虫调度"""
    class_lst = [
        CN4Hours,  # 上证 4 小时
        CNStock,  # 宏观等 ...
    ]

    table_name = 'cn_stock'
    dt_benchmark = 'pub_date'

    def ins_start(self, instance):
        instance.start()

    def thread_start(self):
        ins_list = [cls() for cls in self.class_lst]
        pool = threadpool.ThreadPool(4)
        reqs = threadpool.makeRequests(self.ins_start, ins_list)
        [pool.putRequest(req) for req in reqs]
        pool.wait()

    def start(self):
        for cls in self.class_lst:
            ins = cls()
            ins.start()


if __name__ == "__main__":
    cns = CNSchedule()
    cns.start()
