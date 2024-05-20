#!/usr/bin/python3.10.6
# -*- coding: utf-8 -*-
# @Time    : 2024/5/11 19:56
# @Author  : liuxin22
# @File    : FreqEst.py
# @Software: PyCharm
from tqdm import *
import numpy as np
import random
import mmh3
import math
from collections import defaultdict
from scipy.linalg import hadamard

class FreqEst:
    def __init__(self, k, m, epsilon, datastream, hash_seed):
        self.k = k
        self.m = m
        self.epsilon = epsilon

        self.probability = 2 / (math.pow(math.e, self.epsilon) + 1)  # gamma = Pr[B=1] for randomization

        self.c = (math.pow(math.e, self.epsilon) + 1) / (math.pow(math.e, self.epsilon) - 1)
        self.had = hadamard(self.m)
        self.sketch = np.zeros((self.k, self.m))  # initialize k*m sketch

        self.hash_seed = hash_seed
        self.datastream = datastream
        self.unique_set, self.true_freq = np.unique(self.datastream, return_counts=True)
        # print(self.unique_set)
        self.n = len(self.datastream)

    # client-side
    def _insert(self, item):
        """
        Parameters
        ----------
        item: item being inserted to sketch.

        Returns
        -------
        (j,l): the index that item being inserted to.
        y: the one-bit sent to the server.
        """
        # Encoding step:
        j: int = np.random.randint(0, self.k)
        l: int = np.random.randint(0, self.m)
        v = [0] * self.m
        index_j = mmh3.hash(str(item), self.hash_seed + j, signed=False) % self.m
        v[index_j] = 2 * (mmh3.hash(str(item), self.hash_seed + j + self.k, signed=False) % 2) - 1
        # Hadamard Mechanism:
        w = self.had[:, index_j] * v[index_j]
        x = w[l]
        # Perturbing step:
        if random.random() < self.probability:
            y = random.randint(-1, 1)
        else:
            y = x
        return j, l, y

    # server-side
    # Since the shuffle step is served for privacy amplification, where only the order of reports has changed. We
    # directly insert all reports one-by-one for simplicity.
    # But the shuffle step may influence the efficiency.
    def insert_all(self):
        for i in trange(len(self.datastream), desc='Inserting items to SDPJoinSketch'):
            j, l, y = self._insert(self.datastream[i])
            self.sketch[j, l] += self.k * self.c * y

    def calibrating(self):
        self.sketch = np.matmul(self.sketch, np.transpose(self.had))

    def _frequency_est(self, sketch, value):
        """
        Parameters
        ----------
        sketch: the aggregated and calibrated sketch.
        value: value of unique item.

        Returns
        -------
        est_freq: estimated frequency of unique item.
        """
        sums = 0
        for i in range(self.k):
            index_i = mmh3.hash(str(value), self.hash_seed + i, signed=False) % self.m
            xi = 2 * (mmh3.hash(str(value), self.hash_seed + i + self.k, signed=False) % 2) - 1
            sums += sketch[i, index_i] * xi
        est_freq = 1 / self.k * sums
        return est_freq

    def frequency_est_all(self):
        est_freq = defaultdict(float)
        for uniq_item in self.unique_set:
            ef = self._frequency_est(self.sketch, uniq_item)
            est_freq[uniq_item] = ef
        return est_freq
