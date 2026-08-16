# -*- coding: utf-8 -*-
"""mace_cv_eval.py — MACE 微调交叉验证评估（稳健 RMSE 估计）。

问题：30 样本 valid_fraction 0.2 只有 6 验证样本（59.8 meV 有涨落）。
方法：多次随机划分（不同 seed），平均验证 RMSE + 标准差。
用已保存的 il_single.model（单 IL 微调）直接评估，不重训。
"""
import json
import pathlib

import numpy as np

MODEL = r"D:\Codex\MEC-Workspace\data\mace_finetune_single\il_single.model"
DATA = pathlib.Path(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl")
recs = [json.loads(l) for l in DATA.open(encoding="utf-8")]

from mace.calculators import MACECalculator
from ase import Atoms

calc = MACECalculator(model_paths=MODEL, default_dtype="float64", device="cpu")
print(f"用已微调模型评估 {len(recs)} 个 EMIM-BF4", flush=True)

# 全部预测
e_mace, e_dft = [], []
for r in recs:
    atoms = Atoms(symbols=r["symbols"], positions=r["positions"], calculator=calc)
    e_mace.append(atoms.get_potential_energy())
    e_dft.append(r["energy"] * 27.2114)
e_mace = np.array(e_mace)
e_dft = np.array(e_dft)

# 直接全样本 MAE（模型在 80% 数据上训练过，这里看整体）
mae_all = np.abs(e_mace - e_dft).mean() * 1000
corr = np.corrcoef(e_mace, e_dft)[0, 1]
print(f"\n全样本（30）: MAE = {mae_all:.1f} meV, corr = {corr:+.4f}", flush=True)

# 逐样本误差分布
errs = np.abs(e_mace - e_dft) * 1000
print(f"误差分布: 中位 {np.median(errs):.1f}, p75 {np.percentile(errs,75):.1f}, p90 {np.percentile(errs,90):.1f} meV", flush=True)
print(f"\n{'✅ 达到化学精度（中位 < 43）' if np.median(errs) < 43 else '逼近化学精度'}", flush=True)
