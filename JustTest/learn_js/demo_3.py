import base64

from Crypto.Cipher import AES


class AESCipher(object):
    def __init__(self, key):
        self.bs = 16
        self.cipher = AES.new(key, AES.MODE_ECB)

    def encrypt(self, raw):
        raw = self._pad(raw)
        encrypted = self.cipher.encrypt(raw)
        encoded = base64.b64decode(encrypted)
        return str(encoded, 'utf-8')

    def decrypt(self, raw):
        decoded = base64.b64decode(raw)
        decrypted = self.cipher.decrypt(decoded)
        return str(self._unpad(decrypted), "utf-8")

    def _pad(self, s):
        padded = s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)
        return padded

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]