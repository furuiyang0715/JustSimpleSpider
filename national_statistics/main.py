"""
# 这几个分频道使用的是一个镜像
docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/gov_stats:v0.0.1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/gov_stats:v0.0.1


sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/gov_stats:v0.0.1
sudo /usr/local/bin/docker-compose up -d
use little_crawler
redis = Redis(host='redis', port=6379)

"""
import datetime
import functools
import time

import sys
import traceback
import schedule

sys.path.append("./..")

from national_statistics.configs import MYSQL_TABLE
from national_statistics.my_log import logger


def catch_exceptions(cancel_on_failure=False):
    """
    装饰器, 对定时任务中的异常进行捕获, 并决定是否在异常发生时取消任务
    :param cancel_on_failure:
    :return:
    """
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                logger.warning(traceback.format_exc())
                # sentry.captureException(exc_info=True)
                if cancel_on_failure:
                    logger.warning("异常, 任务结束, {}".format(schedule.CancelJob))
                    schedule.cancel_job(job_func)
                    return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator


@catch_exceptions(cancel_on_failure=True)
def task():
    t1 = time.time()
    if MYSQL_TABLE == "gov_stats_zxfb":
        from national_statistics.gov_stats_zxfb import GovStats
    elif MYSQL_TABLE == "gov_stats_xwfbh":
        from national_statistics.gov_stats_xwfbh import GovStats

    runner = GovStats()
    runner.start()
    logger.info("列表页爬取失败 {}".format(runner.error_list))
    logger.info("详情页爬取失败 {}".format(runner.detail_error_list))
    t2 = time.time()
    logger.info("花费的时间是 {} s".format(t2 - t1))


def main():
    logger.info("启动时第一次开始爬取任务")
    task()

    logger.info("当前时间是{}, 开始增量爬取 ".format(datetime.datetime.now()))
    # schedule.every(180).seconds.do(task)
    schedule.every().day.at("03:00").do(task)
    # schedule.every(5).days.at("05:00").do(task)

    while True:
        logger.info("当前调度系统中的任务列表是{}".format(schedule.jobs))
        schedule.run_pending()
        time.sleep(300)
        logger.info("No work to do, waiting")


main()
