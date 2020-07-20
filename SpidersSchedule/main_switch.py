import functools
import os
import pprint
import sys
import threading
import time
import traceback

import schedule

cur_path = os.path.split(os.path.realpath(__file__))[0]
file_path = os.path.abspath(os.path.join(cur_path, ".."))
sys.path.insert(0, file_path)

from QQStock.qq_stock import qqStock
from StockStcn.kuaixun import STCNSchedule
from CArticle.ca_main import CaSchedule
from Taoguba.tgb_main import TgbSchedule
from ClsCnInfo.telegraphs import Telegraphs
from JfInfo.jfinfo_main import JFSchedule
from JuchaoInfo.juchao import JuChaoInfo
from Money163.netease_money import NetEaseMoney
from ShangHaiSecuritiesNews.cn_main import CNSchedule
from Takungpao.takungpao_main import TakungpaoSchedule
from CalendarNewsRelease.news_release import CalendarNews
from GovSpiders.gov_main import ChinaBankSchedule, GovStatsSchedule
from base import SpiderBase, logger
from configs import LOCAL


def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                logger.warning(traceback.format_exc())
                # sentry.captureException(exc_info=True)
                if cancel_on_failure:
                    logger.warning("异常 任务结束: {}".format(schedule.CancelJob))
                    schedule.cancel_job(job_func)
                    return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator


class MainSwith(SpiderBase):
    def __init__(self):
        super(MainSwith, self).__init__()
        self.tables = list()

    def ding_crawl_information(self):
        self._spider_init()
        print(self.tables)
        msg = ''
        for table, dt_benchmark in self.tables:
            sql = '''SELECT count(id) as inc_count FROM {} WHERE {} > date_sub(CURDATE(), interval 1 day);'''.format(table, dt_benchmark)
            inc_count = self.spider_client.select_one(sql).get("inc_count")
            msg += f'{table} 今日新增 {inc_count}\n'

        if not LOCAL:
            self.ding(msg)
        else:
            print(msg)

    @staticmethod
    def run_threaded(job_func):
        job_thread = threading.Thread(target=job_func)
        job_thread.start()

    def thread_task(self, cls, dt_str, at_once=1):
        @catch_exceptions(cancel_on_failure=True)
        def task():
            self.run_threaded(cls().start)

        self.tables.append((cls.table_name, cls.dt_benchmark))
        if at_once:
            task()
        schedule.every().day.at(dt_str).do(task)

    def start_task(self, cls, dt_str, at_once=1):
        # @catch_exceptions(cancel_on_failure=True)
        def task():
            cls().start()

        self.tables.append((cls.table_name, cls.dt_benchmark))
        if at_once:    # 是否立即执行一遍
            task()
        schedule.every().day.at(dt_str).do(task)

    def run(self):
        self.thread_task(TakungpaoSchedule, "00:00", 1)

        self.thread_task(JFSchedule, '01:00', 1)

        self.thread_task(JuChaoInfo, '02:00', 1)

        self.thread_task(NetEaseMoney, '03:00', 1)

        self.thread_task(CNSchedule, '04:00', 1)

        self.thread_task(Telegraphs, '04:00', 1)

        self.thread_task(CalendarNews, '06:00', 1)

        self.thread_task(ChinaBankSchedule, '07:00', 1)

        self.thread_task(GovStatsSchedule, '08:00', 1)

        self.thread_task(STCNSchedule, '09:00', 1)

        self.thread_task(qqStock, '10:00', 1)

        # self.thread_task(CaSchedule, '05:00', 1)    # 东财财富号：运行时间较长，新开线程去执行；需要代理
        # self.thread_task(TgbSchedule, '16:00', 1)  # 淘股吧：运行时间较长，新开线程去处理; 需要代理

        self.ding_crawl_information()
        schedule.every().day.at("17:00").do(self.ding_crawl_information)

        while True:
            logger.info("当前调度系统中的任务列表是:\n{}".format(pprint.pformat(schedule.jobs)))
            schedule.run_pending()
            time.sleep(10)


if __name__ == "__main__":
    ms = MainSwith()
    ms.run()



'''
docker build -f Dockerfile -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spi:v1 . 
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spi:v1
sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spi:v1 

sudo docker run --log-opt max-size=10m --log-opt max-file=3 -itd \
--env LOCAL=0 \
--name spi_all \
registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/spi:v1 \
python SpidersSchedule/main_switch.py

'''