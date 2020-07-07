import datetime
import functools
import logging
import pprint
import sys
import time
import traceback
import schedule

sys.path.append("./../")
from PublicOpinion.stcn import runner
from PublicOpinion.qq_stock import qqStock
from Money163.netease_money import Money163
from PublicOpinion.configs import FIRST
from PublicOpinion.cn_4_hours import CNStock_2
from PublicOpinion.cn_hongguan import CNStock
from JuchaoInfo.juchao import JuChaoInfo


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


def juchao():
    runner = JuChaoInfo()
    runner.start()
    print("insert error list: {}".format(runner.error_detail))
    with open("record.txt", "a+") as f:
        f.write("juchao: {}\r\n".format(runner.error_detail))


def neteasy():
    m = Money163()
    m.start()
    with open("record.txt", "a+") as f:
        f.write("网易财经: {}\r\n".format(m.error_detail))


def qq_stock():
    d = qqStock()
    d._start()
    with open("h_record.txt", "a+") as f:
        f.write("腾讯财经网页版: {}\r\n".format(d.error_detail))


def cn_stock():
    task_info = {
        'qmt-sns_yw': "要闻-宏观",
        "qmt-sns_jg": "要闻-金融",

        "qmt-scp_gsxw": "公司-公司聚焦",
        "qmt-tjd_ggkx": "公司-公告快讯",
        "qmt-tjd_bbdj": "公司-公告解读",

        "qmt-smk_gszbs": "市场-直播",
        "qmt-sx_xgjj": "市场-新股-新股聚焦",
        "qmt-sx_zcdt": "市场-新股-政策动态",
        "qmt-sx_xgcl": "市场-新股-新股策略",
        "qmt-sx_ipopl": "市场-新股-IPO评论",

        "qmt-smk_jjdx": "市场-基金",
        "qmt-sns_qy": "市场-券业",
        "qmt-smk_zq": "市场-债券",
        "qmt-smk_xt": "市场-信托",

        "qmt-skc_tt": "科创板-要闻",
        "qmt-skc_jgfx": "科创板-监管",
        "qmt-skc_sbgsdt": "科创板-公司",
        "qmt-skc_tzzn": "科创板-投资",
        "qmt-skc_gd": "科创板-观点",
        "qmt-sjrz_yw": "新三板-要闻",
    }
    now = lambda: time.time()
    for topic in task_info:
        print("{} spider strat.".format(task_info.get(topic)))
        t1 = now()
        runner = CNStock(topic=topic)
        runner.start()
        print("{} spider end, use {} s.\n\n".format(
            task_info.get(topic),
            (now() - t1)
        )
        )
        with open("record.txt", "a+") as f:
            f.write(f"{topic}: {runner.error_detail}\r\n")

    # 上证四小时是不同的网页模式
    t2 = now()
    print("{} spider strat.".format("上证4小时"))
    runner = CNStock_2()
    runner.start()
    print("{} spider end, use {} s.\n\n".format(
        "上证4小时",
        (now() - t2)
    )
    )
    with open("record.txt", "a+") as f:
        f.write(f"上证4小时: {runner.error_detail}\r\n")


def hour_task():
    # 记录时间信息
    dt = datetime.datetime.today().strftime("%Y-%m-%d %H-%M-%S")
    with open("h_record.txt", "a+") as f:
        f.write("{}\r\n".format(dt))

    print("开始爬取腾讯财经网页版")
    try:
        qq_stock()
    except:
        traceback.print_exc()
        print("爬取腾讯财经失败")

    with open("h_record.txt", "r") as f:
        ret = f.readlines()
    print(pprint.pformat(ret))


@catch_exceptions(cancel_on_failure=True)
def task():
    # 记录时间信息
    dt = datetime.datetime.today().strftime("%Y-%m-%d")
    with open("record.txt", "a+") as f:
        f.write("{}\r\n".format(dt))

    # print("开始爬取财联社..")
    # cls = ClsSchedule()
    # cls.thread_run()
    # print("爬取财联社结束.. ")

    print("开始爬取证券时报网.. ")
    runner.thread_run()

    print("开始爬取网易财经")
    try:
        neteasy()
    except:
        traceback.print_exc()
        print("爬取网易财经失败")

    print("开始爬取巨潮资讯\n\n")
    try:
        juchao()
    except:
        traceback.print_exc()
        print("爬取巨潮失败")

    print("开始爬取上海证券报\n\n")
    try:
        cn_stock()
    except:
        traceback.print_exc()
        print("爬取上海证券报失败 ")

    with open("record.txt", "r") as f:
        ret = f.readlines()
    print(pprint.pformat(ret))


def main():
    print('【舆情】模块启动时开启一次爬取.')
    task()

    hour_task()

    print("当前时间是{}, 开始【舆情】模块的增量爬取 ".format(datetime.datetime.now()))
    # TODO 监控系统是 9 点开始检查的 所以应该凌晨 5 点就进行检查
    schedule.every().day.at("05:00").do(task)
    schedule.every(5).hours.do(hour_task)

    while True:
        print("【舆情】当前调度系统中的任务列表是{}".format(schedule.jobs))
        schedule.run_pending()
        time.sleep(1800)   # 没有任务时每隔半小时查看一次任务列表


main()
