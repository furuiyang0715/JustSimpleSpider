import threading
from collections import deque
from time import monotonic as time

# from queue import Queue
# 关于线程中的条件变量: https://blog.csdn.net/brucewong0516/article/details/84587522


class Full(Exception):
    # 队列满的异常
    'Exception raised by Queue.put(block=0)/put_nowait().'
    pass


class Empty(Exception):
    'Exception raised by Queue.get(block=0)/get_nowait().'
    pass


class Queue:
    '''Create a queue object with a given maximum size.

    If maxsize is <= 0, the queue size is infinite.
    '''

    def __init__(self, maxsize=0):
        # 队列的最大个数
        self.maxsize = maxsize
        self._init(maxsize)

        # 线程锁
        self.mutex = threading.Lock()

        # Notify not_empty whenever an item is added to the queue; a thread waiting to get is notified then.
        # 当一个项目被添加到队列中时通知not_empty;然后通知等待获取的线程。
        # 在 threading 模块中, Condition被称为条件变量，除了提供与Lock类似的acquire和release方法外，还提供了wait和notify方法。
        self.not_empty = threading.Condition(self.mutex)

        # Notify not_full whenever an item is removed from the queue; a thread waiting to put is notified then.
        # 当从队列中删除项时，通知not_full;然后通知等待put的线程。
        self.not_full = threading.Condition(self.mutex)

        # Notify all_tasks_done whenever the number of unfinished tasks drops to zero; thread waiting to join() is notified to resume
        # 当未完成任务的数量减少到零时通知all_tasks_done;等待join()的线程被通知继续执行
        self.all_tasks_done = threading.Condition(self.mutex)
        self.unfinished_tasks = 0

    def _init(self, maxsize):
        self.queue = deque()

    def _qsize(self):
        # 获取队列的长度
        return len(self.queue)

    def put_nowait(self, item):
        '''Put an item into the queue without blocking.

        Only enqueue the item if a free slot is immediately available.
        Otherwise raise the Full exception.
        '''
        return self.put(item, block=False)

    # Put a new item in the queue
    def _put(self, item):
        self.queue.append(item)

    def put(self, item, block=True, timeout=None):
        '''Put an item into the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until a free slot is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Full exception if no free slot was available within that time.
        Otherwise ('block' is false), put an item on the queue if a free slot
        is immediately available, else raise the Full exception ('timeout'
        is ignored in that case).
        '''
        with self.not_full:
            if self.maxsize > 0:

                if not block:
                    if self._qsize() >= self.maxsize:
                        raise Full

                elif timeout is None:
                    while self._qsize() >= self.maxsize:
                        self.not_full.wait()    # 阻塞等待

                elif timeout < 0:
                    raise ValueError("'timeout' must be a non-negative number")
                else:
                    endtime = time() + timeout
                    while self._qsize() >= self.maxsize:
                        remaining = endtime - time()
                        if remaining <= 0.0:
                            raise Full
                        self.not_full.wait(remaining)

            self._put(item)
            # 在放入的时候 增加队列的 unfinished_tasks 属性
            self.unfinished_tasks += 1
            self.not_empty.notify()

    # Get an item from the queue
    def _get(self):
        return self.queue.popleft()

    def get(self, block=True, timeout=None):
        '''Remove and return an item from the queue.

        If optional args 'block' is true and 'timeout' is None (the default),
        block if necessary until an item is available. If 'timeout' is
        a non-negative number, it blocks at most 'timeout' seconds and raises
        the Empty exception if no item was available within that time.
        Otherwise ('block' is false), return an item if one is immediately
        available, else raise the Empty exception ('timeout' is ignored
        in that case).
        '''
        with self.not_empty:
            if not block:
                if not self._qsize():
                    raise Empty
            elif timeout is None:
                while not self._qsize():
                    self.not_empty.wait()
            elif timeout < 0:
                raise ValueError("'timeout' must be a non-negative number")
            else:
                endtime = time() + timeout
                while not self._qsize():
                    remaining = endtime - time()
                    if remaining <= 0.0:
                        raise Empty
                    self.not_empty.wait(remaining)
            item = self._get()
            self.not_full.notify()
            return item

    def get_nowait(self):
        '''Remove and return an item from the queue without blocking.

        Only get an item if one is immediately available. Otherwise
        raise the Empty exception.
        '''
        return self.get(block=False)

    def empty(self):
        '''Return True if the queue is empty, False otherwise (not reliable!).

        This method is likely to be removed at some point.  Use qsize() == 0
        as a direct substitute, but be aware that either approach risks a race
        condition where a queue can grow before the result of empty() or
        qsize() can be used.

        To create code that needs to wait for all queued tasks to be
        completed, the preferred technique is to use the join() method.
        '''
        with self.mutex:
            return not self._qsize()

    def full(self):
        '''Return True if the queue is full, False otherwise (not reliable!).

        This method is likely to be removed at some point.  Use qsize() >= n
        as a direct substitute, but be aware that either approach risks a race
        condition where a queue can shrink before the result of full() or
        qsize() can be used.
        '''
        with self.mutex:
            return 0 < self.maxsize <= self._qsize()

    def qsize(self):
        '''Return the approximate size of the queue (not reliable!).'''
        with self.mutex:
            return self._qsize()

    def task_done(self):
        '''Indicate that a formerly enqueued task is complete.

        Used by Queue consumer threads.  For each get() used to fetch a task,
        a subsequent call to task_done() tells the queue that the processing
        on the task is complete.

        If a join() is currently blocking, it will resume when all items
        have been processed (meaning that a task_done() call was received
        for every item that had been put() into the queue).

        Raises a ValueError if called more times than there were items
        placed in the queue.
        '''
        with self.all_tasks_done:
            unfinished = self.unfinished_tasks - 1
            if unfinished <= 0:
                if unfinished < 0:
                    raise ValueError('task_done() called too many times')
                self.all_tasks_done.notify_all()
            self.unfinished_tasks = unfinished

    def join(self):
        '''Blocks until all items in the Queue have been gotten and processed.

        The count of unfinished tasks goes up whenever an item is added to the
        queue. The count goes down whenever a consumer thread calls task_done()
        to indicate the item was retrieved and all work on it is complete.

        When the count of unfinished tasks drops to zero, join() unblocks.
        '''
        with self.all_tasks_done:
            while self.unfinished_tasks:
                self.all_tasks_done.wait()


def main():
    q = Queue(10)
    print(q)
    for i in range(10):
        q.put(i)
    print(q)

    for j in range(10):
        print(q.get())
        # q.task_done()

    # q.join()


if __name__ == "__main__":
    main()
