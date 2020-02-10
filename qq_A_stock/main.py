"""
docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/qq_astock:v0.0.1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/qq_astock:v0.0.1


sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/qq_astock:v0.0.1
sudo /usr/local/bin/docker-compose up -d
sudo docker image prune

use little_crawler
"""

import datetime
import functools
import time
import sys
import traceback
import schedule



sys.path.append("./..")

from qq_A_stock.qq_stock import qqStock
from qq_A_stock.my_log import logger
from qq_A_stock.fetch_proxy import proxy_run


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
    proxy_run()
    now = lambda: time.time()
    t1 = now()
    d = qqStock()
    d.start()
    logger.info("花费的时间是 {} s".format(now() - t1))


def main():
    logger.info("启动时第一次开始爬取任务")
    task()

    logger.info("当前时间是{}, 开始增量爬取 ".format(datetime.datetime.now()))
    schedule.every(3).days.at("03:00").do(task)

    while True:
        # logger.info("当前调度系统中的任务列表是{}".format(schedule.jobs))
        schedule.run_pending()
        time.sleep(180)
        # logger.info("No work to do, waiting")


main()
