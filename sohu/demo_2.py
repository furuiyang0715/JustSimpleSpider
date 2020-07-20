import time

_ts = 1595213398000
# _ts = 1595213834525
print(_ts)
print(time.time())
ret = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(_ts / 1000))
print(ret)
