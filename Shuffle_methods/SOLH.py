#!/usr/bin/python3.10.6
# -*- coding: utf-8 -*-
# @Time    : 2024/4/1 14:33
# @Author  : liuxin22
# @File    : SLH.py
# @Software: PyCharm
import numpy as np
import time
import math
import mmh3
import csv
import xxhash
import random
from tqdm import *
from collections import defaultdict

Y = []
class SOLH:
    """
    Shuffler-based optimal local hashing.
    """
    def __init__(self, epsilon, g, datastream):
        """
        Parameters
        ----------
        epsilon: privacy budget, should be positive.
        datastream: dataset for estimation.
        """
        self.epsilon = epsilon
        self.datastream = datastream

        self.n = len(datastream)
        self.unique_set, self.true_freq = np.unique(self.datastream, return_counts=True)

        self.g = g  # Shuffler-based Optimal  Local Hashing setting.

        self.prob_p = math.exp(self.epsilon) / (self.g + math.exp(self.epsilon) - 1)
        self.prob_q = 1.0 / (self.g + math.exp(self.epsilon) - 1)

        self.d = len(self.unique_set)
        self.delta = 1e-9

    def _perturb(self, item, i):
        """
        Parameters
        ----------
        item: item being perturbed.
        """
        global Y
        x = mmh3.hash(str(item), seed=i) % self.g
        y = x
        p_sample = np.random.random_sample()
        if p_sample > self.prob_p - self.prob_q:
            # perturb
            y = np.random.randint(0, self.g)
        Y[i] = y

    def perturbing_all(self):
        global Y
        Y = np.zeros(self.n)
        for i in trange(self.n, desc="Perturbing items in datastream"):
            self._perturb(self.datastream[i], i)

    def aggregate_all(self):
        priv_freq = np.zeros(self.d)
        for i in range(self.n):
            for v in range(self.d):
                if Y[i] == (xxhash.xxh32(str(v), seed=i).intdigest() % self.g):
                    priv_freq[v] += 1
        return priv_freq

    def calibrating(self, priv_freq):
        a = 1.0 * self.g / (self.prob_p * self.g - 1)
        b = 1.0 * self.n / (self.prob_p * self.g - 1)
        cali_freq = a * priv_freq - b
        return cali_freq

    def compute_amplified_eps(self):
        eps_c = 2 * math.sqrt(14 * math.log(4 / self.delta) * (math.exp(self.epsilon / 2) + 1) / (self.n - 1))
        return eps_c

