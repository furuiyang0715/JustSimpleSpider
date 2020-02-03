import hashlib

m5 = hashlib.md5()

m5.update("ruiyang".encode())

ret = m5.hexdigest()

print(ret)
# f4f122f0d6344f425134f6b6521e1108

# 将 16 进制转换为 10 进制
i = int("f", 16)
print(i)  # 15

# 将 10 进制转换为 2 进制
j = bin(i)
print(j)  # 0b1111


