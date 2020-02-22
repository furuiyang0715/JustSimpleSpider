import datetime
import functools
import logging
import time
import traceback

import schedule

logger = logging.getLogger()


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
    pass
    # d = Money163()
    # d.start()


def main():
    logger.info('官媒模块启动时开启一次爬取.')
    task()

    logger.info("当前时间是{}, 开始官媒模块的增量爬取 ".format(datetime.datetime.now()))
    schedule.every().day.at("05:00").do(task)

    while True:
        logger.info("官媒当前调度系统中的任务列表是{}".format(schedule.jobs))
        schedule.run_pending()
        time.sleep(1800)   # 没有任务时每隔半小时查看一次任务列表


main()
