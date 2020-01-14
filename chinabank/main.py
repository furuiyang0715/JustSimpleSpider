"""
定时任务以及日历记录
"""
import functools
import logging
import sys
import time
import schedule


sys.path.insert(0, "./..")
from chinabank.china_bank import ChinaBank

logger = logging.getLogger()


def catch_exceptions(cancel_on_failure=False):
    # 定时任务中的异常捕获
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                import traceback
                logger.warning(traceback.format_exc())
                # sentry.captureException(exc_info=True)
                if cancel_on_failure:
                    # print(schedule.CancelJob)
                    # schedule.cancel_job()
                    return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator


@catch_exceptions(cancel_on_failure=True)
def task():
    runner = ChinaBank()
    runner.start()
    print(runner.error_list)


def main():
    task()

    # schedule.every(5).days.at("05:00").do(task)
    schedule.every().day.at("05:00").do(task)

    while True:
        logger.info(schedule.jobs)
        schedule.run_pending()
        time.sleep(300)
        logger.info("no work to do, waiting")


main()
