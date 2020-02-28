# 财联社主调度程序
import time
import threadpool

import sys
sys.path.append("./../../")
from PublicOpinion.cls_cn.afterAfficheList import afterAfficheList
from PublicOpinion.cls_cn.depth import DepthSchedule
from PublicOpinion.cls_cn.reference import ReferenceSchedule
from PublicOpinion.cls_cn.telegraphs import Telegraphs


now = lambda: time.time()


class ClsSchedule(object):
    def __init__(self):
        self.tele = Telegraphs()
        self.depth_sche = DepthSchedule()
        self.refe_sche = ReferenceSchedule()
        self.after = afterAfficheList()

    def ins_start(self, instance):
        # 开启具体的某个爬虫实例
        instance.start()

    def simple_run(self):
        # 顺序执行
        start_time = now()
        for instance in [self.tele, self.depth_sche, self.after]:
            self.ins_start(instance)
        print("顺序执行所用的时间是{}".format(now() - start_time))  # 大概是 537

    def thread_run(self):
        # 多线程运行
        # 因为这里不涉及使用 代理 ip 所以可以开启多线程
        start_time = now()
        pool = threadpool.ThreadPool(4)
        req = threadpool.makeRequests(self.ins_start, [self.tele, self.depth_sche, self.after])
        [pool.putRequest(r) for r in req]
        pool.wait()
        print("线程池执行所用的时间是{}".format(now() - start_time))  # 大概是 362


cls = ClsSchedule()
# cls.simple_run()

cls.thread_run()




