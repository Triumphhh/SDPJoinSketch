#!/usr/bin/python3.10.6
# -*- coding: utf-8 -*-
# @Time    : 2024/5/17 15:08
# @Author  : liuxin22
# @File    : Laplace.py
# @Software: PyCharm
import numpy as np
import csv
from collections import Counter

def frequency_vector(data_vector):
    freq_counter = Counter(data_vector)
    max_value = max(data_vector)
    return [freq_counter[i] for i in range(max_value + 1)]

def data_gen(file):
    with open(file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        data_vector = [int(row[0]) for row in reader]
    return data_vector

def laplace_mechanism(data_vector, sensitivity, privacy_budget):
    # 计算尺度参数
    scale = sensitivity / privacy_budget
    # 生成拉普拉斯噪声
    noise = np.random.laplace(scale=scale, size=len(data_vector))
    # 添加噪声到数据向量
    noisy_data = data_vector + noise
    return noisy_data

# def add_laplace_noise(value, sensitivity, privacy_budget):
#     scale = sensitivity / privacy_budget
#     noise = np.random.laplace(scale=scale)
#     noisy_value = value + noise
#     return noisy_value


dataset = 'zipf1_1'

if dataset in ['facebook', 'twitter', 'test']:
    filename0 = '../data/' + dataset + '/' + dataset + '.csv'
    filename1 = '../data/' + dataset + '/' + dataset + '.csv'
else:
    filename0 = '../data/' + dataset + '/' + dataset + '_1M_fix500.csv'
    filename1 = '../data/' + dataset + '/' + dataset + '_1M_fix500.csv'

data0 = data_gen(filename0)
data1 = data_gen(filename1)

# 示例数据向量
frequency1 = list(Counter(data0).values())
frequency2 = list(Counter(data1).values())
# print(frequency1)
# print(frequency2)
# Sen = max(max(frequency1), max(frequency2))
Join_Size = sum(x * y for x, y in zip(frequency1, frequency2))


# 设置敏感度为1，隐私预算为0.1
sensitivity = 1
privacy_budget = 0.1

# 添加拉普拉斯噪声
print("adding noise...")
testcycles = 10
t = testcycles
AAE = 0
ARE = 0
while t > 0:
    noisy_data1 = laplace_mechanism(frequency1, sensitivity, privacy_budget)
    noisy_data2 = laplace_mechanism(frequency2, sensitivity, privacy_budget)

    noisy_join_size = np.dot(noisy_data1, noisy_data2)
    # print("原始数据频数:", frequency1)
    # print("添加噪声后的数据向量:", noisy_data1)

    # print("原始数据频数:", frequency2)
    # print("添加噪声后的数据向量:", noisy_data2)

    AE = abs(Join_Size - noisy_join_size)
    RE = AE / Join_Size
    AAE += AE
    ARE += RE
    t = t - 1
    print(t)

AAE /= testcycles
ARE /= testcycles
print("原始数据连接大小:", Join_Size)
# print("添加噪声后的连接大小:", noisy_join_size)
print("AE:", AAE)
print("RE:", ARE)

# t = 10
# AE2 = 0
# RE2 = 0
# while t > 0:
#     noisy_value = add_laplace_noise(Join_Size, Sen, privacy_budget)
#     AE = abs(noisy_value - Join_Size)
#     RE = AE / Join_Size
#     AE2 = AE2 + AE
#     RE2 = RE2 + RE
#     t = t - 1

# t = 10
# AE2 = AE2 / t
# RE2 = RE2 / t
# print("AE2:", AE2)
# print("RE2:", RE2)

