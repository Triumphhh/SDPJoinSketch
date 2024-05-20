#!/usr/bin/python3.10.6
# -*- coding: utf-8 -*-
# @Time    : 2024/5/9 16:26
# @Author  : liuxin22
# @File    : run.py
# @Software: PyCharm
import os

# datasets = ["zipf1_1", "zipf1_2", "zipf1_3", "zipf1_4", "zipf1_5", "zipf1_6", "zipf1_7", "zipf1_8", "zipf1_9", "zipf2_0"]
datasets = ["zipf1_1", "zipf1_5", "zipf2_0"]
# method = "sflh"
# methods = ["skrr", "sflh", "sjs"]
# methods = ["sjsp"]
testcycles = 5
ks = [9]
ms = [64, 128, 256, 512, 1024]
epsilon = [0.5]
# epsilon = [0.5]
hash_seed = 1000
shuffles = [1]
theta = 0.1
rs = [0.1]

for shuffle in shuffles:
    if shuffle == 0:
        methods = ["skrr", "sflh", "sjs"]
        for k in ks:
            for m in ms:
                for r in rs:
                    for dataset in datasets:
                        for method in methods:
                            for i in range(len(epsilon)):
                                eps = epsilon[i]
                                t = testcycles
                                while t > 0:
                                    # hash_seed = hash_seed+1
                                    run_order = f"python shuffleDP.py --dataset {dataset} --k {k} --m {m} --epsilon {eps} " \
                                                f"--seed {hash_seed} --method {method} --shuffle {shuffle} --theta {theta} --r {r}"
                                    t = t - 1
                                    os.system(run_order)
                                    print("The " + str(testcycles - t) + f" times running done while epsilon={eps} for {method}!")

                            print(f"Processes Done while method = {method}.")
    else:
        # methods = ["skrr", "sflh", "sjs"]
        methods = ["sjsp"]
        for k in ks:
            for m in ms:
                for r in rs:
                    for dataset in datasets:
                        for method in methods:
                            for i in range(len(epsilon)):
                                eps = epsilon[i]
                                t = testcycles
                                while t > 0:
                                    # hash_seed = hash_seed + 1
                                    run_order = f"python shuffleDP.py --dataset {dataset} --k {k} --m {m} --epsilon {eps} " \
                                                f"--seed {hash_seed} --method {method} --shuffle {shuffle} --theta {theta} --r {r}"
                                    t = t - 1
                                    os.system(run_order)
                                    print("The " + str(
                                        testcycles - t) + f" times running done while epsilon={eps} for {method}"
                                                          f" in {dataset} at r={r}!")

                            print(f"Processes Done while method = {method}.")
