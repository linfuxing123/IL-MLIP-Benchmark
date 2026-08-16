# -*- coding: utf-8 -*-
"""mace_relative_eval.py — MACE 相对能量评估（对齐参考态）。"""
import json
import pathlib

import numpy as np

DATA = pathlib.Path(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl")
MODEL = r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model"
recs = [json.loads(l) for l in DATA.open(encoding="utf-8")]

from mace.calculators import MACECalculator
from ase import Atoms

calc = MACECalculator(model_paths=MODEL, default_dtype="float64", device="cpu")
print("MACE-MP-0 加载成功", flush=True)

e_mace, e_dft = [], []
for r in recs[:15]:
    atoms = Atoms(symbols=r["symbols"], positions=r["positions"], calculator=calc)
    e_mace.append(atoms.get_potential_energy())  # eV
    e_dft.append(r["energy"] * 27.2114)          # Ha → eV

e_mace = np.array(e_mace)
e_dft = np.array(e_dft)

# 相对能量（各自减均值）：ML 势的核心是预测能量"变化"（力/构型依赖）
e_mace_rel = e_mace - e_mace.mean()
e_dft_rel = e_dft - e_dft.mean()

mae_abs = np.abs(e_mace - e_dft).mean() * 1000
mae_rel = np.abs(e_mace_rel - e_dft_rel).mean() * 1000
corr = np.corrcoef(e_mace_rel, e_dft_rel)[0, 1]

print(f"\n绝对能量 MAE = {mae_abs:.0f} meV（参考态不同，无意义）", flush=True)
print(f"相对能量 MAE = {mae_rel:.0f} meV（构型依赖，有意义）", flush=True)
print(f"相对能量 corr = {corr:+.3f}", flush=True)
print(f"\nDFT 能量涨落: {e_dft_rel.std()*1000:.0f} meV（信号尺度）", flush=True)
print(f"MACE 能量涨落: {e_mace_rel.std()*1000:.0f} meV", flush=True)

if corr > 0.3:
    print(f"\n→ MACE 捕捉到部分构型依赖（corr {corr:+.2f}），微调后有望大幅改善", flush=True)
else:
    print(f"\n→ MACE zero-shot 未捕捉 IL 构型依赖（需微调）", flush=True)
