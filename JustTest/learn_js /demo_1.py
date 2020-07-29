import hashlib
import sys


# def get_ascii():
#     for c in "furuiyang":
#         print(ord(c))
#     print()
#     for word in "沸羊羊":
#         print(ord(word))
#
#
# def get_char():
#     asc_codes = [ord(c) for c in "happy"]
#     for asc_code in asc_codes:
#         print(chr(asc_code), end=',')
#
#
# get_ascii()
# get_char()


# def get_word_md5():
#     """对字符串进行 hash """
#     hm = hashlib.md5()
#     # 进行 md5 的字符必须是 bytes 类型的
#     hm.update("ruiyang".encode())
#     print(hm.hexdigest())
#
#
# def get_file_mds():
#     """对文件进行 hash """
#     hash_md5 = hashlib.md5()
#     with open("./test.txt", "rb") as f:
#         # 每次读取 10 字节的 bytes
#         # 每次读取的大小不对最终的  hash 结果造成影响
#         for chunk in iter(lambda: f.read(10), b""):
#             hash_md5.update(chunk)
#     print(hash_md5.hexdigest())
#
#
# get_word_md5()
# get_file_mds()


# # 对称加密
# import base64
#
# from Crypto.Cipher import AES
#
#
# class AESCipher(object):
#     def __init__(self, key):
#         self.bs = 16
#         self.cipher = AES.new(key, AES.MODE_ECB)
#
#     def encrypt(self, raw):
#         raw = self._pad(raw)
#         encrypted = self.cipher.encrypt(raw)
#         encoded = base64.b64decode(encrypted)
#         return str(encoded, 'utf-8')
#
#     def decrypt(self, raw):
#         decoded = base64.b64decode(raw)
#         decrypted = self.cipher.decrypt(decoded)
#         return str(self._unpad(decrypted), "utf-8")
#
#     def _pad(self, s):
#         padded = s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)
#         return padded
#
#     def _unpad(self, s):
#         return s[:-ord(s[len(s)-1:])]
#
#
# print(AESCipher('aaaabbbbccccddd'))


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



