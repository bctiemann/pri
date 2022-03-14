import base64
import re

from Crypto.Cipher import AES


class AESCipher(object):
    control_chars = ''.join(map(chr, list(range(0, 32)) + list(range(127, 160))))
    control_char_re = re.compile('[%s]' % re.escape(control_chars))

    def __init__(self, key):
        self.bs = 16
        self.cipher = AES.new(base64.b64decode(key), AES.MODE_ECB)

    def encrypt(self, raw):
        raw = self._pad(raw)
        encrypted = self.cipher.encrypt(raw.encode('utf-8'))
        encoded = base64.b64encode(encrypted)
        return str(encoded, 'utf-8')

    def decrypt(self, raw):
        decoded = bytes.fromhex(raw)
        decrypted = self.cipher.decrypt(decoded)
        return self._remove_control_chars(str(self._unpad(decrypted), 'utf-8'))

    def _remove_control_chars(self, s):
        return s
        # return self.control_char_re.sub('', s)

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s):
        if ord(s[len(s)-1:]) > 16:
            return s
        return s[:-ord(s[len(s)-1:])]
