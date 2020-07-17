from queue import Queue
import threading


def add_to_queue():
    for i in range(0, 100):
        print("存入队列: {}".format(i))
        q.put(i)


def get_from_queue():
    # 但是在我们获取队列元素的时候, 我们并不知道队列中放了几个元素,
    # 这个时候我们就会使用while的死循环来获取,知道取完为止
    # for i in range(0, 100):
    while True:
        print("从队列中取出: {}".format(q.get()))
        q.task_done()


q = Queue()
# 创建线程
t1 = threading.Thread(target=add_to_queue)
# 设置为守护线程
t1.setDaemon(True)

t2 = threading.Thread(target=get_from_queue)
t2.setDaemon(True)

# 启动线程
t2.start()
t1.start()

# 队列加入主线线程, 等待队列中任务完成为止
q.join()
