import pprint
import threading
import time
import schedule


def task1():
    print("停留 100 s 的任务 1")
    time.sleep(100)
    print("I'm running on thread %s" % threading.current_thread())
    print("任务 1 结束")


def task2():
    print("停留 10 s 的任务 2")
    time.sleep(10)
    print("I'm running on thread %s" % threading.current_thread())
    print("任务 2 结束")


def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()


def main():
    schedule.every(10).seconds.do(run_threaded, task1)
    schedule.every(10).seconds.do(run_threaded, task2)

    while 1:
        thread_num = len(threading.enumerate())
        print("主线程：线程数量是%d" % thread_num)
        # print(pprint.pformat(schedule.jobs))
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
