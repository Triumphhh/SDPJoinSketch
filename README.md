# SDPJoinSketch

论文 **《Improving Utility of Private Join Size Estimation via Shuffling》** 的实验源代码。

## 项目简介

本仓库实现了一系列在 **本地差分隐私（LDP）** 和 **Shuffle DP** 模型下的隐私保护连接大小估计方法。核心思路是利用 *shuffle 隐私放大* 效应：每个用户在本地以较强的预算 $ε_l$ 添加随机噪声，经过 shuffle 后，中心端获得的有效隐私保证被放大至更小的 $ε_c$，从而在相同中心 DP 预算下大幅提升估计精度。

本文提出两个方法：

- **SDPJoinSketch（SJS）**：用户在本地对 AMS sketch 单元添加 $ε_l$ 噪声，经 shuffle 实现隐私放大；服务端对校准后的两侧 sketch 做内积，取 k 行结果的中位数作为最终估计。
- **SDPJoinSketch+（SJS+）**：在 SJS 基础上引入数据分割策略。先用小比例样本在 LDP 下估计频繁项，频繁项和非频繁项分别建立独立 sketch，合并后输出，显著降低数据分布偏斜时的估计误差。

## 目录结构

```
SDPJoinSketch/
├── shuffleDP.py              # 主入口：数据加载、方法调度、结果输出
├── parameter_setting.py      # 命令行参数解析（argparse）
├── run.py                    # 批量实验运行脚本
├── results/                  # 实验结果 CSV 输出目录
└── Shuffle_methods/
    ├── FAGMS.py              # 无隐私 FAGMS sketch（精度上界 baseline）
    ├── PrivacyAmplify.py     # 隐私放大：由中心 ε_c、n、δ 反算本地 ε_l
    ├── SKRR.py               # 对称 Kroenecker 随机响应（SKRR）
    ├── SFLH.py               # 对称快速局部哈希（SFLH）
    ├── SDPJoinSketch.py      # 提出方法：SJS
    ├── SDPJoinSketch_plus.py # 提出方法：SJS+
    └── FreqEst.py            # SJS+ 频率估计子模块
```

## 方法列表

| 方法标识 | 描述 | 隐私模型 |
|---|---|---|
| `fagms` | 无隐私 AMS sketch，精度上界 baseline | 无 |
| `lap` | 对每个 key 的频率添加 Laplace 噪声 | 中心 DP |
| `skrr` | SKRR 频率估计 + 连接大小估计 | LDP / Shuffle |
| `sflh` | SFLH 频率估计 + 连接大小估计 | LDP / Shuffle |
| `sjs` | **SDPJoinSketch**（本文提出） | LDP / Shuffle |
| `sjsp` | **SDPJoinSketch+**（本文提出，适应数据倾斜） | Shuffle |

## 环境依赖

Python 3.10+，依赖如下：

```
numpy
```

安装：

```bash
pip install numpy
```

## 数据格式

每个数据集文件为单列 CSV，每行一个整数值，无表头。文件放置于 `data/<数据集名>/` 目录下：

```
data/
└── zipf1_1/
    └── zipf1_1_1M_fix500.csv
```

`facebook` 和 `twitter` 数据集的文件名直接为 `<数据集名>.csv`。

## 使用方法

### 单次运行

```bash
python shuffleDP.py \
  --dataset zipf1_1 \
  --method sjs \
  --shuffle 1 \
  --epsilon 1.0 \
  --k 9 \
  --m 256 \
  --delta 1e-9 \
  --seed 1000 \
  --mode run
```

### 参数说明

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `--dataset` | str | — | 数据集名称（对应 `data/` 下的子目录） |
| `--method` | str | — | 运行方法（`fagms` / `lap` / `skrr` / `sflh` / `sjs` / `sjsp`） |
| `--shuffle` | int | `0` | `1` 启用 Shuffle 模型，`0` 为纯 LDP |
| `--epsilon` | float | `1.0` | 中心隐私预算 $ε_c$ |
| `--delta` | float | `1e-9` | (ε, δ)-DP 的失败概率 δ |
| `--k` | int | `18` | sketch 行数（独立哈希函数数量） |
| `--m` | int | `256` | sketch 列数（每行桶数） |
| `--seed` | int | `1000` | 哈希随机种子，用于复现实验 |
| `--r` | float | `0.1` | SJS+ 频率估计阶段的采样比例 |
| `--theta` | float | `0.1` | SJS+ 识别频繁项的频率阈值 |
| `--mode` | str | `run` | `run` 将结果写入 CSV；`test` 仅打印输出 |

### 批量实验

按需修改 `run.py` 中的参数网格，然后执行：

```bash
python run.py
```

实验结果以追加模式写入 `results/results.csv`，列格式为：

```
shuffle, dataset, method, k, m, epsilon, seed, ground_truth, estimate, AE, RE, time
```

## 隐私预算计算

`PrivacyAmplify` 模块接受中心预算 ($ε_c$, $δ$) 和数据集大小 n，反算出使 shuffle 协议满足 ($ε_c$, $δ$)-DP 所需的本地预算 $ε_l$。当 `--shuffle 1` 时，该模块会针对两侧数据集分别自动计算并应用对应的本地噪声强度。

## 评估指标

每次运行输出以下指标：

- **AE（绝对误差）**：|真实连接大小 − 估计值|
- **RE（相对误差）**：AE / 真实连接大小
- **运行时间**（秒）

## 引用

如果本代码对您的研究有帮助，请引用对应论文：

```bibtex
@article{Liu2025ImprovingUO,
  title={Improving Utility of Private Join Size Estimation via Shuffling},
  author={Xin Liu and Yibin Mao and Meifan Zhang and Mohan Li},
  journal={Mathematics},
  year={2025}
}
```
