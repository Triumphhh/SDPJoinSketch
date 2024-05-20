#!/usr/bin/python3.10.6
# -*- coding: utf-8 -*-
# @Time    : 2024/5/8 9:32
# @Author  : liuxin22
# @File    : parameter_setting.py
# @Software: PyCharm
import argparse
import warnings

def get_args():
    """
    Initializing parameters.
    """
    parser = argparse.ArgumentParser()

    # type int
    parser.add_argument("--k", type=int, default=18, help="number of hash functions")
    parser.add_argument("--m", type=int, default=256, help="domain size of sketch")
    parser.add_argument("--seed", type=int, default=1000, help="hash_seed")
    parser.add_argument("--shuffle", type=int, default=0, help="whether shuffle differential privacy used")

    # type float
    parser.add_argument("--epsilon", type=float, default=1, help="privacy budget")
    parser.add_argument("--r", type=float, default=0.1, help="sample rate for LDPJoinSketch+")
    parser.add_argument("--theta", type=float, default=0.1, help="threshold of high frequency")
    parser.add_argument("--delta", type=float, default=1e-9, help="failure probability")

    # type str
    parser.add_argument("--dataset", type=str, default="", help="dataset name")
    parser.add_argument("--method", type=str, default="", help="method used")
    parser.add_argument("--mode", type=str, default="run", help="experiments mode")

    args = parser.parse_args()
    if args.epsilon < 0:
        raise argparse.ArgumentTypeError('epsilon should be greater than 0!')
    # if args.epsilon > 10:
    #     warnings.warn('epsilon is too large to protect privacy!')

    return args
