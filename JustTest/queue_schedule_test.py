import queue
import time
import threading
import schedule


def task1():
    print("停留 100 s 的任务 1")
    time.sleep(100)
    print("任务 1 结束")


def task2():
    print("停留 10 s 的任务 2")
    time.sleep(10)
    print("任务 2 结束")


def worker_main():
    while 1:
        job_func = jobqueue.get()
        job_func()
        '''
        如果线程里每从队列里取一次，但没有执行task_done()，则join无法判断队列到底有没有结束，在最后执行个join()是等不到结果的，会一直挂起。
        可以理解为，每task_done一次 就从队列里删掉一个元素，这样在最后join的时候根据队列长度是否为零来判断队列是否结束，从而执行主线程。
        '''
        jobqueue.task_done()


if __name__ == "__main__":
    jobqueue = queue.Queue()
    schedule.every(10).seconds.do(jobqueue.put, task1)
    schedule.every(10).seconds.do(jobqueue.put, task2)
    worker_thread = threading.Thread(target=worker_main)
    worker_thread.start()

    while 1:
        print("队列中的任务数量是: ", jobqueue.qsize())
        schedule.run_pending()
        time.sleep(1)
