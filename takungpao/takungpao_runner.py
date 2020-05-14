import threadpool

from takungpao import Business
from takungpao import DiChan
from takungpao import EconomicObserver
from takungpao import GuoJiJingJi
from takungpao import HKStock
from takungpao import HKCaiJing
from takungpao import HKStock_CJSS
from takungpao import HKStock_GJJJ
from takungpao import HKStock_GSYW
from takungpao import HKStock_JGSD
from takungpao import HKStock_JJYZ
from takungpao import HKStock_QQGS
from takungpao import NewFinanceTrend
from takungpao import FK
from takungpao import Travel
from takungpao import ZhongGuoJingJi


class TakungpaoSchedule(object):

    def ins_start(self, instance):
        instance.start()

    def start(self):
        class_lst = [
            Business,  # 商业
            DiChan,  # 地产
            EconomicObserver,   # 经济观察家
            GuoJiJingJi,  # 国际经济
            HKStock,  # 港股
            HKCaiJing,  # 香港财经
            HKStock_CJSS,  # 财经时事
            HKStock_GJJJ,  # 国际聚焦
            HKStock_GSYW,  # 公司要闻
            HKStock_JGSD,   # 机构视点
            HKStock_JJYZ,   # 经济一周
            HKStock_QQGS,  # 全球股市
            NewFinanceTrend,   # 新经济浪潮
            FK,   # 风口
            Travel,  # 旅游
            ZhongGuoJingJi,  # 中国经济
        ]

        # # just test
        # for cls in class_lst:
        #     ins = cls()
        #     print(ins.name)

        # instance 列表
        ins_list = [cls() for cls in class_lst]

        pool = threadpool.ThreadPool(4)
        reqs = threadpool.makeRequests(self.ins_start, ins_list)
        [pool.putRequest(req) for req in reqs]
        pool.wait()


if __name__ == "__main__":

    sche = TakungpaoSchedule()
    sche.start()
