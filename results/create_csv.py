#!/usr/bin/python3.10.6
# -*- coding: utf-8 -*-
# @Time    : 2024/5/8 9:59
# @Author  : liuxin22
# @File    : create_csv.py
# @Software: PyCharm
import csv
with open("results.csv", "w", encoding="gbk", newline="") as f:
    csv_writer = csv.writer(f)
    csv_writer.writerow(["Shuffle", "Dataset", "Method", "k", "m/hash_d", "epsilon", "hash_seed", "TrueRes", "EstRes",
                         "AE", "RE", "RunTime"])
    print("write_done")
    f.close()
