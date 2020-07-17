# import threading
#
#
# class XiaoAi(threading.Thread):
#     def __init__(self, lock):
#         super().__init__(name="小爱")
#         self.lock = lock
#
#     def run(self):
#         self.lock.acquire()
#         print("{} : 在".format(self.name))
#         self.lock.release()
#
#         self.lock.acquire()
#         print("{} : 好啊".format(self.name))
#         self.lock.release()
#
#
# class TianMao(threading.Thread):
#     def __init__(self, lock):
#         super().__init__(name="天猫精灵")
#         self.lock = lock
#
#     def run(self):
#         self.lock.acquire()
#         print("{} : 小爱同学".format(self.name))
#         self.lock.release()
#
#         self.lock.acquire()
#         print("{} : 我们来对古诗吧".format(self.name))
#         self.lock.release()
# if __name__ == "__main__":
#     lock = threading.Lock()
#     xiaoai = XiaoAi(lock)
#     tianmao = TianMao(lock)
#
#     tianmao.start()
#     xiaoai.start()


'''
使用互斥锁来实现小爱和天猫之间的对话
输出结果并不是预期的对话顺序，这是因为天猫精灵的线程说完“小爱同学”之后，cpu的控制权还没有交出去，继续获取了互斥锁，又执行了“我们来对古诗吧”，所以不能得到预期结果。

假设有一个全局变量active_user，为0表示该A线程执行，1表示B线程执行，对于A线程，先实现wait方法：就是while循环判断是否active_user == 0（必须保证这个变量在两个线程中使用的是同一个），
notify方法：将 active_user 赋值为 1。对于B线程，实现方式相反。


'''


import threading


class XiaoAi(threading.Thread):
    def __init__(self, lock, active_user):
        super().__init__(name="小爱")
        self.lock = lock
        self.active_user = active_user

    def wait(self):
        while(1):
            self.lock.acquire()
            user = self.active_user[0]
            self.lock.release()
            if user == 1:
                break

    def notify(self):
        self.lock.acquire()
        self.active_user[0] = 0
        self.lock.release()

    def run(self):
        self.wait()
        print("{} : 在".format(self.name))
        self.notify()

        self.wait()
        print("{} : 好啊".format(self.name))
        self.notify()


class TianMao(threading.Thread):
    def __init__(self, lock, active_user):
        super().__init__(name="天猫精灵")
        self.lock = lock
        self.active_user = active_user

    def wait(self):
        while True:
            self.lock.acquire()
            user = self.active_user[0]
            self.lock.release()
            if user == 0:
                break

    def notify(self):
        self.lock.acquire()
        self.active_user[0] = 1
        self.lock.release()

    def run(self):
        self.wait()
        print("{} : 小爱同学".format(self.name))
        self.notify()

        self.wait()
        print("{} : 我们来对古诗吧".format(self.name))
        self.notify()


if __name__ == "__main__":
    # 0表示天猫执行， 1表示小爱
    # 为了保证两个线程修改active_user之后,互相是可见的，所以传了一个List,而不是整数
    active_user = [0]
    lock = threading.Lock()
    xiaoai = XiaoAi(lock, active_user)
    tianmao = TianMao(lock, active_user)

    tianmao.start()
    xiaoai.start()
