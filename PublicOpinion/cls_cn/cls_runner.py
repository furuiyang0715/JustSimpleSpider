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
        instance.start()

    def simple_run(self):
        # start_time = now()
        for instance in [
            self.tele,
            self.depth_sche,
            self.after,
        ]:
            self.ins_start(instance)
        # print("顺序执行所用的时间是{}".format(now() - start_time))  # 大概是 537

    # def thread_run(self):
    #     start_time = now()
    #     pool = threadpool.ThreadPool(4)
    #     req = threadpool.makeRequests(self.ins_start, [self.tele, self.depth_sche, self.after])
    #     [pool.putRequest(r) for r in req]
    #     pool.wait()
    #     print("线程池执行所用的时间是{}".format(now() - start_time))  # 大概是 362


if __name__ == "__main__":
    cls = ClsSchedule()
    cls.simple_run()
