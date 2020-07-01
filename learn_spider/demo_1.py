# str 与 bytes 之间的相互转换
s = '中国'
print(s)

ret1 = s.encode()
print(ret1)

ret2 = s.encode("utf-8")
print(ret2)

print(ret1 == ret2)

ret3 = ret1.decode()
print(ret3)

ret4 = ret2.decode("utf-8")
print(ret3 == ret4)

_gbk = s.encode("GBK")
print(_gbk)
ret5 = _gbk.decode("GBK")
print(ret5)
