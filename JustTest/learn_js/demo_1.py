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



# # 使用字母表移位的方式进行简单的加密以及解密
# def _move_leter(letter, n):
#     """
#     把字母变为字母表后n位的字母,z后面接a
#     :param letter: 小写字母
#     :param n: 要移动的字母
#     :return: 移动的结果
#     """
#     _first = ord("a")
#     _instance = ord(letter) - _first
#     _new_instance = (_instance + n) % 26
#     _new_char = chr(_new_instance + _first)
#     return _new_char
#
#     # return chr((ord(letter) - ord('a') + n) % 26 + ord('a'))
#
#
# def Encrypt(k, p):
#     """
#     移位密码加密函数E
#     :param k: 秘钥k,每个字母在字母表中移动k位
#     :param p: 明文p
#     :return: 密文c
#     """
#     letter_list = list(p.lower())
#     c = ''.join([_move_leter(x, k) for x in letter_list])
#     return c
#
#
# def Decrypt(k, c):
#     """
#     移位密码解密函数D
#     :param k: 秘钥k,每个字母在字母表中移动k位
#     :param c: 密文c
#     :return: 明文p
#     """
#     letter_list = list(c.lower())
#     p = ''.join([_move_leter(x, -k) for x in letter_list])
#     return p
#
#
# if __name__ == '__main__':
#     p = 'ilovecoding'
#     print('明文：' + p)
#     print('密文：' + Encrypt(1, p))
#     print('解密：' + Decrypt(1, Encrypt(1, p)))
#     assert Decrypt(1, Encrypt(1, p)) == p


# def _move_leter(letter, n):
#     """
#     把字母变为字母表后n位的字母,z后面接a
#     :param letter: 小写字母
#     :param n: 要移动的字母
#     :return: 移动的结果
#     """
#     _first = ord("a")
#     _instance = ord(letter) - _first
#     _new_instance = (_instance + n) % 26
#     _new_char = chr(_new_instance + _first)
#     return _new_char
#
#     # return chr((ord(letter) - ord('a') + n) % 26 + ord('a'))
#
#
# def Decrypt(k, c):
#     """
#     移位密码解密函数D
#     :param k: 秘钥k,每个字母在字母表中移动k位
#     :param c: 密文c
#     :return: 明文p
#     """
#     letter_list = list(c.lower())
#     p = ''.join([_move_leter(x, -k) for x in letter_list])
#     return p
#
#
# def analyze(c):
#     """
#     移位密码分析
#     :param c: 密文c
#     :return:
#     """
#     for k in range(26):
#         # 用不同的秘钥k尝试解密
#         print('秘钥%d：' % k + Decrypt(k, c))
#
#
# if __name__ == '__main__':
#     # 模拟一个破解的过程 尝试不同的位移进行破解
#     # 秘钥空间太小，别人直接一一列举进行穷搜就能破解，这就提示我们：一个好的加密体制，它的秘钥空间应该是足够大的。
#     c = 'jmpwfdpejoh'
#     analyze(c)
