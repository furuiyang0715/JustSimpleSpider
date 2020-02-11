"""
定时任务以及日历记录
docker build -t registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/chinabank:v0.0.1 .
docker push registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/chinabank:v0.0.1

sudo docker pull registry.cn-shenzhen.aliyuncs.com/jzdev/jzdata/chinabank:v0.0.1
sudo /usr/local/bin/docker-compose up -d
sudo docker logs -ft --tail 1000 china_bank
sudo docker image prune

use little_crawler

"""
import datetime
import functools
import sys
import time
import traceback

import schedule

sys.path.insert(0, "./..")
from chinabank.my_log import logger
from chinabank.china_bank_shujujiedu import ChinaBankShuJuJieDu
from chinabank.chinabank_xinwenfabu import ChinaBankXinWenFaBu


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

    now = lambda: time.time()

    for C in [ChinaBankShuJuJieDu, ChinaBankXinWenFaBu]:
        runner = C()
        logger.info("{} 爬虫程序开始爬取了".format(runner.name))
        t1 = now()
        runner.start()
        logger.info("本次爬取耗时 {}".format(now() - t1))
        logger.info("本次未成功爬取的列表页是 {} ".format(runner.error_list))
        logger.info("本次未成功爬取的详情页是 {} ".format(runner.error_detail))

        logger.info("")

    logger.info("任务结束...")


def main():
    logger.info("启动时第一次开始爬取任务")
    task()

    logger.info("当前时间是{}, 开始增量爬取 ".format(datetime.datetime.now()))
    schedule.every().day.at("05:00").do(task)

    while True:
        # logger.info("当前调度系统中的任务列表是{}".format(schedule.jobs))
        schedule.run_pending()
        time.sleep(1800)
        # logger.info("No work to do, waiting")


main()
