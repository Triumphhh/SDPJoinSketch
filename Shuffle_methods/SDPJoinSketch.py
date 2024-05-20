#!/usr/bin/python3.10.6
# -*- coding: utf-8 -*-
# @Time    : 2024/5/9 15:30
# @Author  : liuxin22
# @File    : SDPJoinSketch.py
# @Software: PyCharm
import numpy as np
from collections import defaultdict
import random
import mmh3
from tqdm import *
import math
from scipy.linalg import hadamard

class SDPJoinSketch:
    def __init__(self, k, m, epsilon, datastream, hash_seed):
        """
        Parameters
        ----------
        k: the number of hash_funcs.
        m: the domain size of hash_funcs.
        epsilon: privacy budget.
        datastream: dataset for estimation.
        """
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
        self.n = len(self.datastream)

    def true_frequency(self):  # type defaultdict to compute join size
        tr_fre = defaultdict(int)
        tr_fre.clear()
        for i in range(self.n):
            tr_fre[self.datastream[i]] += 1
        return tr_fre

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
        return self.sketch
