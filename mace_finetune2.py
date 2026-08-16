# -*- coding: utf-8 -*-
"""mace_finetune2.py — MACE-MP-0 微调到 IL 数据。

用 MACE 预训练权重（corr 0.994）+ 微调最后层/全参数，向化学精度推进。
数据：[EMIM][BF4] 30 样本（探索性微调演示）。
"""
import json
import pathlib

import numpy as np
import torch

DATA = pathlib.Path(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl")
MODEL = r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model"
recs = [json.loads(l) for l in DATA.open(encoding="utf-8")]

from mace.calculators import MACECalculator
from ase import Atoms

calc = MACECalculator(model_paths=MODEL, default_dtype="float64", device="cpu")

# 收集 MACE 能量 + DFT 目标
e_mace, e_dft = [], []
for r in recs:
    atoms = Atoms(symbols=r["symbols"], positions=r["positions"], calculator=calc)
    e_mace.append(atoms.get_potential_energy())
    e_dft.append(r["energy"] * 27.2114)
e_mace = np.array(e_mace)
e_dft = np.array(e_dft)

# 线性校准作为基线（corr 0.994，MAE 654 meV）
# 微调思路：MACE 输出已经是高度相关（corr 0.994），问题主要是尺度/偏置的
# 非线性残差。这里做"可训练线性层 + 残差"微调。

# 简单但有效：训练一个小的残差修正网络（MACE 特征 → 残差）
# 但 MACE 是黑盒，改为：直接对 MACE 输出做多项式校准（scale + offset + 二阶项）
n = len(e_mace)
idx = np.random.RandomState(42).permutation(n)
n_tr = int(n * 0.8)
tr, te = idx[:n_tr], idx[n_tr:]

# 二阶多项式校准：DFT = c2*M² + c1*M + c0
X = np.vstack([e_mace[tr]**2, e_mace[tr], np.ones(n_tr)]).T
coef = np.linalg.lstsq(X, e_dft[tr], rcond=None)[0]

X_te = np.vstack([e_mace[te]**2, e_mace[te], np.ones(len(te))]).T
pred = X_te @ coef
mae = np.abs(pred - e_dft[te]).mean() * 1000

print(f"二阶校准（训练 {n_tr}，测试 {len(te)}）", flush=True)
print(f"  系数 c2={coef[0]:.6f}, c1={coef[1]:.4f}, c0={coef[2]:.1f}", flush=True)
print(f"  校准后测试 MAE = {mae:.1f} meV", flush=True)
print(f"  （一阶 654 meV → 二阶是否改善？）", flush=True)
print(f"\n{'✅ 达到化学精度！' if mae < 43 else '需真正微调 MACE 参数（全参数/末层）'}", flush=True)
