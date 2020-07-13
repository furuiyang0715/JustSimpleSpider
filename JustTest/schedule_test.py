import pprint
import time

import schedule


def task1():
    print("停留 100 s 的任务 1")
    time.sleep(100)
    print("任务 1 结束")


def task2():
    print("停留 10 s 的任务 2")
    time.sleep(10)
    print("任务 2 结束")


def main():
    schedule.every(10).seconds.do(task1)
    schedule.every(10).seconds.do(task2)

    while True:
        print("当前调度系统中的任务列表是:\n{}".format(pprint.pformat(schedule.jobs)))
        schedule.run_pending()
        time.sleep(10)


if __name__ == "__main__":
    """schedule 非并行"""
    main()
