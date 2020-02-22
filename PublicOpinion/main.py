import datetime
import functools
import logging
import sys
import time
import traceback
import schedule

from PublicOpinion.cn_4_hours import CNStock_2

sys.path.append("./../")
from PublicOpinion.configs import FIRST


logger = logging.getLogger()

first = FIRST  # 确定是第一次全量爬取还是后续增量爬取


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
    # 上海证券报
    print("开始爬取上海证券报")
    print("当前模块是【上海证券报】-【上证4小时】")
    try:
        runner = CNStock_2()  # 上证4小时
        runner.start()
        print("上海证券报失败的列表页:{}".format(runner.error_list))
        print("上海证券报失败的详情页:{}".format(runner.error_detail))
    except:
        traceback.print_exc()
        print("异常 \n")


def main():
    print('【舆情】模块启动时开启一次爬取.')
    task()

    print("当前时间是{}, 开始【舆情】模块的增量爬取 ".format(datetime.datetime.now()))
    schedule.every().day.at("10:00").do(task)

    while True:
        print("【舆情】当前调度系统中的任务列表是{}".format(schedule.jobs))
        schedule.run_pending()
        time.sleep(1800)   # 没有任务时每隔半小时查看一次任务列表


main()
