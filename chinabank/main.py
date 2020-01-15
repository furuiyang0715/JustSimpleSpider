"""
定时任务以及日历记录
"""
import datetime
import functools
import sys
import time
import traceback

import schedule

sys.path.insert(0, "./..")
from chinabank.china_bank import ChinaBank
from chinabank.my_log import logger


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
    # import random
    # i = random.randint(1, 10)
    # logger.info("i is {}".format(i))
    # if i > 5:
    #     raise RuntimeError("运行异常")

    runner = ChinaBank()
    runner.start()
    logger.info("本次未成功爬取的页面是 {} ".format(runner.error_list))


def main():
    logger.info("启动时第一次开始爬取任务")
    task()

    logger.info("当前时间是{}, 开始增量爬取 ".format(datetime.datetime.now()))
    schedule.every(1800).seconds.do(task)
    # schedule.every().day.at("05:00").do(task)
    # schedule.every(5).days.at("05:00").do(task)

    while True:
        logger.info("当前调度系统中的任务列表是{}".format(schedule.jobs))
        # TODO 如果该列表为空 需要发出上报
        schedule.run_pending()
        time.sleep(10)
        logger.info("No work to do, waiting")


main()
