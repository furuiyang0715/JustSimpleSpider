import threadpool

from JfInfo.reference import HKInfo, Reference, Research, TZZJY
from base import logger


class JFSchedule(object):
    """巨丰财经 爬虫调度"""
    class_lst = [
        HKInfo,  # 港股资讯
        Reference,  # 巨丰内参
        Research,  # 巨丰研究院
        TZZJY,  # 投资者教育
    ]

    table_name = 'jfinfo'
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
            logger.info(f"巨丰财经 --> {ins.name}")
            ins.start()


if __name__ == "__main__":
    sche = JFSchedule()
    sche.start()
