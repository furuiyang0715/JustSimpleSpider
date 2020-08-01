import sys
from binascii import b2a_hex, a2b_hex

from Crypto import Random
from Crypto.Cipher import AES


class AesEncryption(object):
    def __init__(self, key, mode=AES.MODE_CFB):
        self.key = self.check_key(key)
        # 密钥 key 长度必须为16,24或者32bytes的长度
        self.mode = mode
        self.iv = Random.new().read(AES.block_size)

    def check_key(self, key):
        """
        检测 key 的长度是否为 16,24 或者 32bytes 的长度
        :param key:
        :return:
        """
        try:
            if isinstance(key, bytes):
                assert len(key) in [16, 24, 32]
                return key
            elif isinstance(key, str):
                assert len(key.encode()) in [16, 24, 32]
                return key.encode()
            else:
                raise Exception(f'密钥必须为str或bytes,不能为{type(key)}')
        except AssertionError:
            print('输入的长度不正确')

    def check_data(self, data):
        """
        检测进行加密的数据类型
        :param data:
        :return:
        """
        if isinstance(data, str):
            data = data.encode()
        elif isinstance(data, bytes):
            pass
        else:
            raise Exception(f'加密的数据必须为str或bytes,不能为{type(data)}')
        return data

    def encrypt(self, data):
        """
        加密
        :param data:
        :return:
        """
        data = self.check_data(data)
        cryptor = AES.new(self.key, self.mode, self.iv)
        return b2a_hex(cryptor.encrypt(data)).decode()

    def decrypt(self, data):
        """
        解密
        :param data:
        :return:
        """
        data = self.check_data(data)
        cryptor = AES.new(self.key, self.mode, self.iv)
        return cryptor.decrypt(a2b_hex(data)).decode()


if __name__ == '__main__':
    key = b'a' * 16
    data = '你真帅'
    aes = AesEncryption(key)
    e = aes.encrypt(data)  # 调用加密函数
    d = aes.decrypt(e)  # 调用解密函数
    print(e)
    print(d)
