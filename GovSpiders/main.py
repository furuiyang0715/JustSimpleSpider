import datetime
import functools
import logging
import sys
import time
import traceback

import schedule

sys.path.append("./../")
from GovSpiders.configs import FIRST
from GovSpiders.china_bank import ChinaBankShuJuJieDu, ChinaBankXinWenFaBu
from GovSpiders.gov_stats_sjjd import GovStatsShuJuJieDu
from GovSpiders.gov_stats_tjdt import GovStatsTongJiDongTai
from GovSpiders.gov_stats_xwfbh import GovStatsXinWenFaBuHui
from GovSpiders.gov_stats_zxfb import GovStatsZuiXinFaBu

logger = logging.getLogger()
print("First is ", FIRST)  # 确定是第一次全量爬取还是后续增量爬取


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
    print("当前模块[中国银行]-[数据解读]")
    try:
        chinabank_shujufenxi = ChinaBankShuJuJieDu()
        if FIRST:
            for page in range(1, 25):
                chinabank_shujufenxi.start(page)
        else:
            chinabank_shujufenxi.start(1)
        print("[中国银行]-[数据解读]失败列表页: {}".format(chinabank_shujufenxi.error_list))
        print("[中国银行]-[数据解读]失败详情页: {} ".format(chinabank_shujufenxi.error_detail))
        print("[中国银行]-[数据解读]本次插入个数: {}: ".format(chinabank_shujufenxi.nums))
    except:
        print("模块[中国银行]-[数据解读]开启失败\n")

    print("当前模块[中国银行]-[新闻发布]")
    try:
        chinabank_xinwenfabu = ChinaBankXinWenFaBu()
        if FIRST:
            for page in range(1, 265):
                chinabank_xinwenfabu.start(page)
        else:
            chinabank_xinwenfabu.start(1)
        print("[中国银行]-[新闻发布]失败列表页: {}".format(chinabank_xinwenfabu.error_list))
        print("[中国银行]-[新闻发布]失败列表页: {} ".format(chinabank_xinwenfabu.error_detail))
        print("[中国银行]-[新闻发布]本次插入个数: {} ".format(chinabank_xinwenfabu.nums))
    except:
        print("模块[中国银行]-[新闻发布]开启失败\n")

    # &&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

    print("当前模块[国家统计局]-[数据解读]")
    try:
        gov_shujujiedu = GovStatsShuJuJieDu()
        if FIRST:
            for page in range(1, 6):
                gov_shujujiedu.start(page)
        else:
            gov_shujujiedu.start(1)
        print("[国家统计局]-[数据解读]失败列表页: {} ".format(gov_shujujiedu.error_list))
        print("[国家统计局]-[数据解读]失败列表页: {} ".format(gov_shujujiedu.error_detail))
        print("[国家统计局]-[数据解读]本次插入个数 : {} ".format(gov_shujujiedu.nums))
    except:
        print("[国家统计局]-[数据解读] 开启失败\n")

    print("当前模块[国家统计局]-[统计动态]")
    try:
        gov_tongjidongtai = GovStatsTongJiDongTai()
        if FIRST:
            for page in range(1, 6):
                gov_tongjidongtai.start(page)
        else:
            gov_tongjidongtai.start(1)
        print("[国家统计局]-[统计动态]失败列表页: {} ".format(gov_tongjidongtai.error_list))
        print("[国家统计局]-[统计动态]失败列表页: {} ".format(gov_tongjidongtai.error_detail))
        print("[国家统计局]-[统计动态]本次插入个数: {} ".format(gov_tongjidongtai.nums))
    except:
        print("[国家统计局]-[统计动态] 开启失败\n")

    print("当前模块[国家统计局]-[新闻发布会]")
    try:
        gov_xinwenfabuhui = GovStatsXinWenFaBuHui()
        if FIRST:
            for page in range(1, 6):
                gov_xinwenfabuhui.start(page)
        else:
            gov_xinwenfabuhui.start(1)
        print("[国家统计局]-[新闻发布会]失败列表页: {} ".format(gov_xinwenfabuhui.error_list))
        print("[国家统计局]-[新闻发布会]失败列表页: {} ".format(gov_xinwenfabuhui.error_detail))
        print("[国家统计局]-[新闻发布会]本次插入个数: {} ".format(gov_xinwenfabuhui.nums))
    except:
        print("[国家统计局]-[新闻发布会] 开启失败\n")

    print("当前模块[国家统计局]-[最新发布]")
    try:
        gov_zuixinfabu = GovStatsZuiXinFaBu()
        if FIRST:
            for page in range(1, 6):
                gov_zuixinfabu.start(page)
        else:
            gov_zuixinfabu.start(1)
        print("[国家统计局]-[最新发布]失败列表页: {}".format(gov_zuixinfabu.error_list))
        print("[国家统计局]-[最新发布]失败列表页: {}".format(gov_zuixinfabu.error_detail))
        print("[国家统计局]-[最新发布]本次插入个数: {}".format(gov_zuixinfabu.nums))
    except:
        print("[国家统计局]-[最新发布] 开启失败\n")


def main():
    print('官媒模块启动时开启一次爬取.')
    task()

    print("当前时间是{}, 开始官媒模块的增量爬取 ".format(datetime.datetime.now()))
    schedule.every().day.at("05:00").do(task)

    while True:
        print("官媒当前调度系统中的任务列表是{}".format(schedule.jobs))
        schedule.run_pending()
        time.sleep(1800)


main()
