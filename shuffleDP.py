#!/usr/bin/python3.10.6
# -*- coding: utf-8 -*-
# @Time    : 2024/4/1 14:32
# @Author  : liuxin22
# @File    : shuffleDP.py
# @Software: PyCharm
import math
import time
import csv
import numpy as np
import statistics
import parameter_setting as ps
from collections import defaultdict
from collections import Counter

from Shuffle_methods.FAGMS import FAGMS
from Shuffle_methods.PrivacyAmplify import privacyAmplify
from Shuffle_methods.SKRR import SKRR
from Shuffle_methods.SFLH import SFLH
from Shuffle_methods.SDPJoinSketch import SDPJoinSketch
from Shuffle_methods.SDPJoinSketch_plus import SDPJoinSketch_plus
from Shuffle_methods.FreqEst import FreqEst

def data_gen(file):
    with open(file, 'r') as csvfile:
        reader = csv.reader(csvfile)
        data_vector = [int(row[0]) for row in reader]
    return data_vector

def get_result_by_freq(datastream0, datastream1):
    freq0 = defaultdict(int)
    for i in range(len(datastream0)):
        freq0[datastream0[i]] += 1
    freq1 = defaultdict(int)
    for i in range(len(datastream1)):
        freq1[datastream1[i]] += 1
    true_join_size = 0
    for key, val in freq0.items():
        if key in freq1:
            true_join_size += val * freq1[key]
    return true_join_size

def fagms_example(k, m, datastream0, datastream1, hash_seed):
    fagms0 = FAGMS(k, m, datastream0, hash_seed)
    fagms1 = FAGMS(k, m, datastream1, hash_seed)
    sketch0 = fagms0.insert_all()
    sketch1 = fagms1.insert_all()

    k_est_join_size = np.zeros(k, dtype=np.int64)
    for i in range(k):
        k_est_join_size[i] = np.dot(sketch0[i], sketch1[i])
    est_join_size = statistics.median(k_est_join_size)
    return est_join_size

def skrr_example(is_shuffle, eps_c, delta, datastream0, d0, datastream1, d1):
    if is_shuffle == 1:
        amp0 = privacyAmplify(eps_c, len(datastream0), delta, d0)
        amp1 = privacyAmplify(eps_c, len(datastream1), delta, d1)
        eps_l0 = amp0.eps_l()
        eps_l1 = amp1.eps_l()
        skrr0 = SKRR(eps_l0, datastream0)
        skrr1 = SKRR(eps_l1, datastream1)
    else:
        skrr0 = SKRR(eps_c, datastream0)
        skrr1 = SKRR(eps_c, datastream1)
    skrr0.perturbing_all()
    priv_f0 = skrr0.get_frequency()
    r0 = skrr0.calibrating(priv_f0)
    skrr1.perturbing_all()
    priv_f1 = skrr1.get_frequency()
    r1 = skrr1.calibrating(priv_f1)
    est_join_size = 0
    for key, val in r0.items():
        if key in r1:
            est_join_size += val * r1[key]
    return est_join_size

def sflh_join_sketch_example(is_shuffle, eps_c, k, m, delta, datastream0, datastream1):
    # optimal_g0 = math.floor((math.exp(eps_c)**2 * (len(datastream0)-1)) / (42 * math.log(2/delta)) + 2/3)
    # optimal_g1 = math.floor((math.exp(eps_c)**2 * (len(datastream1)-1)) / (42 * math.log(2/delta)) + 2/3)
    if is_shuffle == 1:
        od0 = math.floor((eps_c ** 2 * (len(datastream0) - 1)) / (42 * math.log(2 / delta)) + 2 / 3)
        od1 = math.floor((eps_c ** 2 * (len(datastream1) - 1)) / (42 * math.log(2 / delta)) + 2 / 3)
        amp0 = privacyAmplify(eps_c, len(datastream0), delta, od0)
        amp1 = privacyAmplify(eps_c, len(datastream1), delta, od1)
        eps_l0 = amp0.eps_l()
        eps_l1 = amp1.eps_l()
        sflh0 = SFLH(eps_l0, datastream0, k, m)
        sflh1 = SFLH(eps_l1, datastream1, k, m)
    else:
        sflh0 = SFLH(eps_c, datastream0, k, round(math.exp(eps_c) + 1))
        sflh1 = SFLH(eps_c, datastream1, k, round(math.exp(eps_c) + 1))

    sflh0.perturbing_all()
    priv_f0 = sflh0.aggregate()
    r0 = sflh0.calibrating(priv_f0)
    sflh1.perturbing_all()
    priv_f1 = sflh1.aggregate()
    r1 = sflh1.calibrating(priv_f1)

    est_join_size = 0
    for key, val in r0.items():
        if key in r1:
            est_join_size += val * r1[key]
    return est_join_size

def sdp_join_sketch_example(is_shuffle, k, m, eps_c, delta, datastream0, datastream1, hash_seed):
    if is_shuffle == 1:
        amp0 = privacyAmplify(eps_c, len(datastream0), delta, 2)
        amp1 = privacyAmplify(eps_c, len(datastream1), delta, 2)
        eps_l0 = amp0.eps_l()
        eps_l1 = amp1.eps_l()
        sjs0 = SDPJoinSketch(k, m, eps_l0, datastream0, hash_seed)
        sjs1 = SDPJoinSketch(k, m, eps_l1, datastream1, hash_seed)
    else:
        sjs0 = SDPJoinSketch(k, m, eps_c, datastream0, hash_seed)
        sjs1 = SDPJoinSketch(k, m, eps_c, datastream1, hash_seed)

    sjs0.insert_all()
    sk0 = sjs0.calibrating()
    sjs1.insert_all()
    sk1 = sjs1.calibrating()
    k_est_join_size = np.zeros(k, dtype=np.int64)
    for i in range(k):
        k_est_join_size[i] = sum(x * y for x, y in zip(sk0[i], sk1[i]))
    est_join_size = np.median(k_est_join_size)
    return est_join_size

def frequency_est(k, m, eps_c, delta, s_datastream0, s_datastream1, hash_seed):
    amp0 = privacyAmplify(eps_c, len(s_datastream0), delta, 2)
    amp1 = privacyAmplify(eps_c, len(s_datastream1), delta, 2)
    eps_l0 = amp0.eps_l()
    eps_l1 = amp1.eps_l()
    print(eps_l0, eps_l1)
    freq_est0 = FreqEst(k, m, eps_l0, s_datastream0, hash_seed)
    freq_est1 = FreqEst(k, m, eps_l1, s_datastream1, hash_seed)
    freq_est0.insert_all()
    freq_est0.calibrating()
    freq_est1.insert_all()
    freq_est1.calibrating()

    s_freq0 = freq_est0.frequency_est_all()
    s_freq1 = freq_est1.frequency_est_all()
    return s_freq0, s_freq1

def frequent_item_set(s_freq0, s_freq1, theta):
    threshold0 = int(theta * sum(s_freq0.values()))
    threshold1 = int(theta * sum(s_freq1.values()))
    print(threshold0, threshold1)
    candidate_h0 = []
    candidate_h1 = []
    for key, value in s_freq0.items():
        if value >= threshold0:
            candidate_h0.append(key)
    for key, value in s_freq1.items():
        if value >= threshold1:
            candidate_h1.append(key)
    fi = list(set(candidate_h0).intersection(set(candidate_h1)))
    print(candidate_h0)
    print(candidate_h1)
    print(f"FI={fi}")
    print(f"len of FI: {len(fi)}")
    return fi

def split_data(datastream, ratio):
    split_point = int(len(datastream) * ratio)
    s_data = datastream[:split_point]
    r_data = datastream[split_point:]
    return s_data, r_data

def sdp_join_sketch_plus_example(k, m, eps_c, delta, datastream0, r_datastream0, datastream1, r_datastream1,
                                 freq_item_set, hash_seed):
    amp0 = privacyAmplify(eps_c, len(r_datastream0), delta, 2)
    amp1 = privacyAmplify(eps_c, len(r_datastream1), delta, 2)
    eps_l0 = amp0.eps_l()
    eps_l1 = amp1.eps_l()
    sjsp0 = SDPJoinSketch_plus(k, m, eps_l0, r_datastream0, freq_item_set, hash_seed)
    sjsp1 = SDPJoinSketch_plus(k, m, eps_l1, r_datastream1, freq_item_set, hash_seed)
    sjsp0.insert_all()
    sjsp1.insert_all()
    sk_h0, sk_l0 = sjsp0.calibrating()
    sk_h1, sk_l1 = sjsp1.calibrating()
    h_k_est_join_size = np.zeros(k, dtype=np.int64)
    l_k_est_join_size = np.zeros(k, dtype=np.int64)
    for i in range(k):
        h_k_est_join_size[i] = sum(x * y for x, y in zip(sk_h0[i], sk_h1[i]))
        l_k_est_join_size[i] = sum(x * y for x, y in zip(sk_l0[i], sk_l1[i]))
    h_est_join_size = np.median(h_k_est_join_size)
    l_est_join_size = np.median(l_k_est_join_size)
    est_join_size = (h_est_join_size + l_est_join_size) * (len(datastream0) * len(datastream1)) / \
                    (len(r_datastream0) * len(r_datastream1))
    return est_join_size

def laplace(eps_c, datastream0, datastream1):
    # 每个桶的灵敏度为1
    sensitivity = 1
    # 计算Laplace噪声的尺度参数
    scale = sensitivity / eps_c
    freq0 = defaultdict(int)
    for i in range(len(datastream0)):
        freq0[datastream0[i]] += 1
    freq1 = defaultdict(int)
    for i in range(len(datastream1)):
        freq1[datastream1[i]] += 1

    priv_freq0 = defaultdict(float)
    for key, count in freq0.items():
        # 为当前桶生成Laplace噪声
        noise = np.random.laplace(0, scale)
        # 更新加噪后的桶计数
        priv_freq0[key] = count + noise

    priv_freq1 = defaultdict(float)
    for key, count in freq1.items():
        # 为当前桶生成Laplace噪声
        noise = np.random.laplace(0, scale)
        # 更新加噪后的桶计数
        priv_freq1[key] = count + noise
    est_join_size = 0
    for key, val in priv_freq0.items():
        if key in priv_freq1:
            est_join_size += val * priv_freq1[key]
    return est_join_size


def main():
    args = ps.get_args()
    hash_k = args.k
    hash_m = args.m
    eps = args.epsilon  # central eps for observation
    r = args.r  # sample rate
    theta = args.theta  # threshold for high-frequent
    method = args.method
    hash_seed = args.seed
    delta = args.delta
    is_shuffled = args.shuffle
    mode = args.mode

    # the file path needs to be modified according to your own environment.
    if args.dataset in ['facebook', 'twitter', 'test']:
        filename0 = 'data/' + args.dataset + '/' + args.dataset + '.csv'  # '_10M_fix.csv'
        filename1 = 'data/' + args.dataset + '/' + args.dataset + '.csv'  # '_10M_fix.csv'
    else:
        filename0 = 'data/' + args.dataset + '/' + args.dataset + '_1M_fix500.csv'  # '_10M_fix.csv'
        filename1 = 'data/' + args.dataset + '/' + args.dataset + '_1M_fix500.csv'  # '_10M_fix.csv'
    data0 = data_gen(filename0)
    data1 = data_gen(filename1)
    d0 = len(set(data0))
    d1 = len(set(data1))
    # print(len(data0), d0, len(data1), d1)
    Join_Ground_Truth = get_result_by_freq(data0, data1)

    st_time = time.time()
    if method in ["fagms", "FAGMS"]:
        eps = 0
        est_joinsize = fagms_example(hash_k, hash_m, data0, data1, hash_seed)
    elif method in ["skrr", "SKRR"]:
        hash_k, hash_m = 0, 0
        est_joinsize = skrr_example(is_shuffled, eps, delta, data0, d0, data1, d1)
    elif method in ["sflh", "SFLH"]:
        est_joinsize = sflh_join_sketch_example(is_shuffled, eps, hash_k, hash_m, delta, data0, data1)
    elif method in ["sjs", "SDPJoinSketch"]:
        est_joinsize = sdp_join_sketch_example(is_shuffled, hash_k, hash_m, eps, delta, data0, data1, hash_seed)
    elif method in ['sjsp', "SDPJoinSketch_plus"]:
        s_data0, r_data0 = split_data(data0, r)
        s_data1, r_data1 = split_data(data1, r)
        # print(len(s_data0), len(s_data1))
        s_freq0, s_freq1 = frequency_est(hash_k, hash_m, eps, delta, s_data0, s_data1, hash_seed)
        freq_item_set = frequent_item_set(s_freq0, s_freq1, theta)
        est_joinsize = sdp_join_sketch_plus_example(hash_k, hash_m, eps, delta, data0, r_data0, data1, r_data1,
                                                    freq_item_set, hash_seed)
    elif method in ['lap', 'Laplace']:
        est_joinsize = laplace(eps, data0, data1)
    else:
        raise ValueError("Invalid method.")

    AE = abs(Join_Ground_Truth - est_joinsize)
    RE = AE / Join_Ground_Truth
    ed_time = time.time()
    total_time = ed_time - st_time

    if mode == 'run':
        # write results to csv file.
        with open("results/results.csv", "a+", encoding="gbk", newline="") as f:
            csv_writer = csv.writer(f)
            csv_writer.writerow([is_shuffled, args.dataset, method, hash_k, hash_m, eps, hash_seed, Join_Ground_Truth,
                                 est_joinsize, AE, RE, total_time])
            f.close()

        print(f"Join Ground Truth: {Join_Ground_Truth}")
        print(f"Est Res: {est_joinsize:.2e}")
        print(f"AE of {method}: {AE}")
        print(f"RE of {method}: {RE}")
        print(f"running time: {total_time} s")
    elif mode == 'test':
        print(f"Join Ground Truth: {Join_Ground_Truth}")
        print(f"Est Res: {est_joinsize:.2e}")
        print(f"AE of {method}: {AE}")
        print(f"RE of {method}: {RE}")
        print(f"running time: {total_time} s")
        print("Test done!")
    else:
        raise ValueError("Invalid mode.")


if __name__ == "__main__":
    main()
