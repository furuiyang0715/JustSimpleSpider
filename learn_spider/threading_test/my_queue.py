'''
可以把Condiftion理解为一把高级的琐，它提供了比Lock, RLock更高级的功能，允许我们能够控制复杂的线程同步问题。
threadiong.Condition在内部维护一个琐对象（默认是RLock），可以在创建Condigtion对象的时候把琐对象作为参数传入。
Condition也提供了acquire, release方法，其含义与琐的acquire, release方法一致，其实它只是简单的调用内部琐对象的对应的方法而已。
Condition还提供wait方法、notify方法、notifyAll方法(特别要注意：这些方法只有在占用琐(acquire)之后才能调用，否则将会报RuntimeError异常。)：

acquire()/release()：获得/释放 Lock

wait([timeout]):线程挂起，直到收到一个notify通知或者超时（可选的，浮点数，单位是秒s）才会被唤醒继续运行。
wait()必须在已获得Lock前提下才能调用，否则会触发RuntimeError。调用wait()会释放Lock，直至该线程被Notify()、NotifyAll()或者超时线程又重新获得Lock.

notify(n=1):通知其他线程，那些挂起的线程接到这个通知之后会开始运行，默认是通知一个正等待该condition的线程,最多则唤醒n个等待的线程。
notify()必须在已获得Lock前提下才能调用，否则会触发RuntimeError。notify()不会主动释放Lock。

notifyAll(): 如果wait状态线程比较多，notifyAll的作用就是通知所有线程（这个一般用得少）
'''
'''
现在写个捉迷藏的游戏来具体介绍threading.Condition的基本使用。假设这个游戏由两个人来玩，一个藏(Hider)，一个找(Seeker)。
游戏的规则如下：
1. 游戏开始之后，Seeker先把自己眼睛蒙上，蒙上眼睛后，就通知Hider；
2. Hider接收通知后开始找地方将自己藏起来，藏好之后，再通知Seeker可以找了； 
3. Seeker接收到通知之后，就开始找Hider。Hider和Seeker都是独立的个体，在程序中用两个独立的线程来表示，在游戏过程中，两者之间的行为有一定的时序关系，我们通过Condition来控制这种时序关系。

'''


import threading
import time


def Seeker(cond, name):
    time.sleep(2)
    cond.acquire()
    print('%s :我已经把眼睛蒙上了！'% name)
    cond.notify()
    cond.wait()

    for i in range(3):
        print('%s is finding!!!'% name)
        time.sleep(2)

    print('%s :我赢了！' % name)
    cond.notify()
    cond.release()


def Hider(cond, name):
    cond.acquire()
    cond.wait()

    for i in range(2):
        print('%s is hiding!!!'% name)
        time.sleep(3)
    print('%s :我已经藏好了，你快来找我吧！'% name)
    cond.notify()
    cond.wait()

    print('%s :被你找到了，唉~^~!' % name)
    cond.release()


if __name__ == '__main__':
    cond = threading.Condition()
    seeker = threading.Thread(target=Seeker, args=(cond, 'seeker'))
    hider = threading.Thread(target=Hider, args=(cond, 'hider'))
    seeker.start()
    hider.start()
