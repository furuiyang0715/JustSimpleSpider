from queue import Queue

q = Queue()
q.put("ruiyang")
print(q.get())
q.task_done()
q.join()
