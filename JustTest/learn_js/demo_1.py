import hashlib
import sys


# 注：两位十六进制常常用来显示一个二进制字节
# 利用binascii模块可以将十六进制显示的字节转换成我们在加解密中更常用的显示方式：
import binascii

print('南北'.encode())
print(binascii.b2a_hex('南北'.encode()))

print(binascii.a2b_hex(b'e58d97e58c97'))
print(binascii.a2b_hex(b'e58d97e58c97').decode())


# 导入DES模块
import binascii
from Crypto.Cipher import DES

# 这是密钥
key = b'abcdefgh'
# 需要去生成一个DES对象
des = DES.new(key, DES.MODE_ECB)
# 需要加密的数据
text = 'python spider!'
text = text + (8 - (len(text) % 8)) * '='

# 加密的过程
encrypto_text = des.encrypt(text.encode())
encrypto_text = binascii.b2a_hex(encrypto_text)
print(encrypto_text)

decrypto_text = des.decrypt(encrypto_text)
print(decrypto_text)
