import pprint

import schedule
import time


def job():
    print("I'm working...")


def job1(name):
    print(name)


def main():
    """模块简单使用"""
    schedule.every(10).minutes.do(job)  # 每10分钟执行一次
    schedule.every().hour.do(job)  # 每小时执行一次
    schedule.every().day.at("10:30").do(job)  # 每天10:30执行一次
    schedule.every().monday.do(job)  # 每周星期一执行一次
    schedule.every().wednesday.at("13:15").do(job)  # 每周星期三执行一次
    schedule.every().wednesday.at("13:15").do(job1, 'waiwen')  # 传入参数

    while True:
        print("当前调度系统中的任务列表是:\n{}".format(pprint.pformat(schedule.jobs)))
        schedule.run_pending()
        time.sleep(10)


if __name__ == "__main__":

    main()
