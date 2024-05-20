#!/usr/bin/python3.10.6
# -*- coding: utf-8 -*-
# @Time    : 2024/5/10 21:36
# @Author  : liuxin22
# @File    : Encryption.py
# @Software: PyCharm
from Crypto.Cipher import AES
from Crypto.Util import Counter
from Crypto.Random import get_random_bytes
import sys
import random

data = [0, 0, 0, 1, 0, 1, 0, 0, 0]
encry = []
nonces = []
decry = []
key = get_random_bytes(16)  # AES的密钥 #使用同一组密钥？
for item in data:
    # 加密过程
    plaintext = str(item).encode()  # 转换为字符串后再转换为字节字符串
    nonce = get_random_bytes(8)  # 生成一个nonce(number used once)
    ctr = Counter.new(64, prefix=nonce)
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)  # CTR计数器模式
    e = cipher.encrypt(plaintext)
    encry.append(e)
    nonces.append(nonce)
    # print("Encrypted data:", e)
    # print("Encrypted data:", e.hex())

# simulating the shuffle step
indices = list(range(len(encry)))
random.shuffle(indices)
encry = [encry[i] for i in indices]
nonces = [nonces[i] for i in indices]

for i in range(len(encry)):
    # 解密过程
    e = encry[i]
    nonce = nonces[i]
    ctr = Counter.new(64, prefix=nonce)
    cipher = AES.new(key, AES.MODE_CTR, counter=ctr)
    decrypted_text = cipher.decrypt(e)
    # print("Decrypted text:", decrypted_text.decode())
    decry.append(int(decrypted_text.decode()))

print(f"Origin data: {data}")
print(f"Encrypt result: {encry}")
print(f"nonce: {nonces}")
print(f"Decrypt result: {decry}")
