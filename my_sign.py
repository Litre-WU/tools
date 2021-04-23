# -*- coding: utf-8 -*-
# Author: Litre WU
# E-mail: litre-wu@tutanota.com
# Software: PyCharm
# File: my_sign.py
# Time: 4月 23, 2021
from random import sample
from Cryptodome.Cipher import AES
from binascii import b2a_hex, a2b_hex


# 加密
def encrypt(*args):
    text = args[0]
    add = 16 - (len(text.encode()) % 16) if len(text.encode()) % 16 else 0
    text = text + ' ' * add
    # 加密
    key = "".join(sample('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 16))
    encrypt_value = b2a_hex(AES.new(key.encode(), AES.MODE_ECB).encrypt(text.encode())).decode()
    return key, encrypt_value


# 解密
def decrypt(**kwargs):
    key, encrypt_value = kwargs.popitem()
    decrypt_value = AES.new(key.encode(), AES.MODE_ECB).decrypt(a2b_hex(encrypt_value)).decode().strip()
    return decrypt_value


if __name__ == '__main__':
    text = '来了，老弟！'
    key, value = encrypt(text)
    print(key, value)
    value = decrypt(**{key: value})
    print(value)
