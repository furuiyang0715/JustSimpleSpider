# import threading
# import time
#
#
# def task():
#     print("我是需要使用多线程去完成的任务")
#     time.sleep(30)
#     print("线程任务结束")
#
#
# def main():
#     th1 = threading.Thread(target=task)
#     th1.setDaemon(True)
#     th1.start()
#     print("Main over")
# main()


import queue
import traceback

q = queue.Queue(maxsize=100)


def queue_test1():
    for i in range(100):
        q.put(i)

    item = {}
    try:
        q.put_nowait(item)  # 不等待直接放，队列满的时候会报错
    except Exception:
        print(traceback.print_exc())


def queue_test2():
    for i in range(100):
        q.put(i)

    item = "ruiyang"
    q.put(item)  # 放入数据，队列满的时候阻塞等待


def queue_test3():
    for i in range(100):
        q.put(i)

    for j in range(100):
        print(q.get())
        # q.task_done()

    q.join()  # 队列中维持了一个计数，计数不为0时候让主线程阻塞等待，队列计数为0的时候才会继续往后执行
    # put的时候计数+1，get不会-1，get需要和task_done 一起使用才会-1
    print("*********** ")


queue_test3()
