#!/usr/bin/python3.10.6
# -*- coding: utf-8 -*-
# @Time    : 2024/4/9 11:03
# @Author  : liuxin22
# @File    : PrivacyAmplify.py
# @Software: PyCharm

import math

class privacyAmplify:
    def __init__(self, eps_c, n, delta, d):
        self.eps_c = eps_c
        self.n = n
        self.delta = delta
        self.d = d

    # def epsl_SOLH(self):
    #     hash_d = self.d
    #     eps_l = math.log((((self.n-1) * self.eps_c**2) / (14 * math.log(2 / self.delta))) - hash_d + 1)
    #     return eps_l
    #
    # def epsl_SKRR(self):
    #     validate = (((self.n - 1) * self.eps_c ** 2) / (14 * math.log(2 / self.delta))) - self.d + 1
    #     if validate <= 0:
    #         raise ValueError(f"Invalide eps_C = {self.eps_c} for validate = {validate}.")
    #     eps_l = math.log(validate)
    #     return eps_l
    #
    # def epsl_SDPJoinSketch(self):
    #     eps_l = math.log((((self.n - 1) * self.eps_c ** 2) / (14 * math.log(2 / self.delta))) - d + 1)
    #     return eps_l

    def eps_l(self):
        eps_l = math.log((((self.n - 1) * self.eps_c ** 2) / (14 * math.log(2 / self.delta))) - self.d + 1)
        return eps_l

    @staticmethod
    def validate(delta, eps_c, n):
        max_d = (((n - 1) * eps_c ** 2) / (14 * math.log(2 / delta))) + 1
        return max_d

    @staticmethod
    def eps_c(delta, eps_l, d, n):
        eps_c = math.sqrt((14 * math.log(2/delta) * (math.exp(eps_l) + d - 1)) / (n - 1))
        return eps_c