import threadpool
from Takungpao.economic_observer import EconomicObserver
from Takungpao.hkstock_cjss import HKStock_CJSS, HKStock_GJJJ, HKStock_GSYW, HKStock_JGSD, HKStock_JJYZ, HKStock_QQGS
from Takungpao.takungpao_fk import FK
from Takungpao.takungpao_travel import Travel
from Takungpao.zhongguojingji import Business, DiChan, GuoJiJingJi, HKStock, HKCaiJing, NewFinanceTrend, ZhongGuoJingJi
from base import logger


class TakungpaoSchedule(object):
    """大公报 爬虫调度"""
    class_lst = [
        Business,  # 商业
        DiChan,  # 地产
        EconomicObserver,  # 经济观察家
        GuoJiJingJi,  # 国际经济
        HKStock,  # 港股
        HKCaiJing,  # 香港财经
        HKStock_CJSS,  # 财经时事
        HKStock_GJJJ,  # 国际聚焦
        HKStock_GSYW,  # 公司要闻
        HKStock_JGSD,  # 机构视点
        HKStock_JJYZ,  # 经济一周
        HKStock_QQGS,  # 全球股市
        NewFinanceTrend,  # 新经济浪潮
        FK,  # 风口
        Travel,  # 旅游
        ZhongGuoJingJi,  # 中国经济
    ]

    table_name = 'Takungpao'
    dt_benchmark = 'pub_date'

    def ins_start(self, instance):
        instance.start()

    def thread_start(self):
        """开启多线程"""
        ins_list = [cls() for cls in self.class_lst]
        pool = threadpool.ThreadPool(4)
        reqs = threadpool.makeRequests(self.ins_start, ins_list)
        [pool.putRequest(req) for req in reqs]
        pool.wait()

    def start(self):
        """顺次运行"""
        for cls in self.class_lst:
            ins = cls()
            logger.info(f"大公报 --> {ins.name}")
            ins.start()
