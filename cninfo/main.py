import datetime
import functools
import logging
import sys
import time
import traceback

import schedule

sys.path.append("./../")
from cninfo.juchao import JuChaoInfo

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def catch_exceptions(cancel_on_failure=False):
    def catch_exceptions_decorator(job_func):
        @functools.wraps(job_func)
        def wrapper(*args, **kwargs):
            try:
                return job_func(*args, **kwargs)
            except:
                print(traceback.format_exc())
                if cancel_on_failure:
                    print("异常, 任务结束, {}".format(schedule.CancelJob))
                    schedule.cancel_job(job_func)
                    return schedule.CancelJob
        return wrapper
    return catch_exceptions_decorator


@catch_exceptions(cancel_on_failure=True)
def task():
    runner = JuChaoInfo()
    runner.start()


def main():
    print("启动时第一次开始爬取任务")
    task()

    print("当前时间是{}, 开始增量爬取 ".format(datetime.datetime.now()))
    schedule.every().day.at("10:00").do(task)

    while True:
        print("当前调度系统中的任务列表是{}".format(schedule.jobs))
        schedule.run_pending()
        time.sleep(1800)


main()
