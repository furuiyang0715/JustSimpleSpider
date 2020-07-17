'''
Python提供的Condition对象提供了对复杂线程同步问题的支持。
Condition被称为条件变量，除了提供与Lock类似的acquire和release方法外，还提供了wait和notify方法。
Condition的处理流程如下：
首先acquire一个条件变量，然后判断一些条件。
如果条件不满足则wait；
如果条件满足，进行一些处理改变条件后，通过notify方法通知其他线程，其他处于wait状态的线程接到通知后会重新判断条件。
不断的重复这一过程，从而解决复杂的同步问题。


演示条件变量同步的经典问题是生产者与消费者问题：假设有一群生产者(Producer)和一群消费者（Consumer）通过一个市场来交互产品。
生产者的”策略“是如果市场上剩余的产品少于1000个，那么就生产100个产品放到市场上；而消费者的”策略“是如果市场上剩余产品的数量多余100个，
那么就消费3个产品。用Condition解决生产者与消费者问题的代码如下：

'''

# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 17:15:29 2018

@author: 18665
"""

import threading
import time


class Producer(threading.Thread):
    # 生产者函数
    def run(self):
        global count
        while True:
            if con.acquire():
                # 当count 小于等于1000 的时候进行生产
                if count > 1000:
                    con.wait()
                else:
                    count = count + 100
                    msg = self.name + ' produce 100, count=' + str(count)
                    print(msg)
                    # 完成生成后唤醒waiting状态的线程，
                    # 从waiting池中挑选一个线程，通知其调用acquire方法尝试取到锁
                    con.notify()
                con.release()
                time.sleep(1)


class Consumer(threading.Thread):
    # 消费者函数
    def run(self):
        global count
        while True:
            # 当 count 大于等于100的时候进行消费
            if con.acquire():
                if count < 100:
                    con.wait()
                else:
                    count = count - 5
                    msg = self.name + ' consume 5, count=' + str(count)
                    print(msg)
                    con.notify()
                    # 完成生成后唤醒waiting状态的线程，
                    # 从waiting池中挑选一个线程，通知其调用acquire方法尝试取到锁
                con.release()
                time.sleep(1)


# 条件变量
count = 500
con = threading.Condition()


def main():
    for i in range(2):
        p = Producer()
        p.start()

    for i in range(5):
        c = Consumer()
        c.start()


if __name__ == '__main__':
    main()
