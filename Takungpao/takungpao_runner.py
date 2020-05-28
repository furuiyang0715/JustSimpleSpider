import threadpool

from takungpao.business import Business
from takungpao.dichan import DiChan
from takungpao.economic_observer import EconomicObserver
from takungpao.guojijingji import GuoJiJingJi
from takungpao.hk_stock import HKStock
from takungpao.hkcaijing import HKCaiJing
from takungpao.hkstock_cjss import HKStock_CJSS
from takungpao.hkstock_gjjj import HKStock_GJJJ
from takungpao.hkstock_gsyw import HKStock_GSYW
from takungpao.hkstock_jgsd import HKStock_JGSD
from takungpao.hkstock_jjyz import HKStock_JJYZ
from takungpao.hkstock_qqgs import HKStock_QQGS
from takungpao.new_finance_trend import NewFinanceTrend
from takungpao.takungpao_fk import FK
from takungpao.takungpao_travel import Travel
from takungpao.zhongguojingji import ZhongGuoJingJi


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

        ins_list = [cls() for cls in class_lst]

        pool = threadpool.ThreadPool(4)
        reqs = threadpool.makeRequests(self.ins_start, ins_list)
        [pool.putRequest(req) for req in reqs]
        pool.wait()


if __name__ == "__main__":
    sche = TakungpaoSchedule()
    sche.start()
