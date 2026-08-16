# -*- coding: utf-8 -*-
"""mace_calibrate.py — MACE 线性校准：zero-shot + 线性映射 → 化学精度？

若 MACE 相对能量与 DFT 相对能量线性相关（corr 0.988），
则简单线性回归（scale + offset）就能校准到化学精度，无需微调。
"""
import json
import pathlib

import numpy as np

DATA = pathlib.Path(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl")
MODEL = r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model"
recs = [json.loads(l) for l in DATA.open(encoding="utf-8")]

from mace.calculators import MACECalculator
from ase import Atoms

calc = MACECalculator(model_paths=MODEL, default_dtype="float64", device="cpu")

e_mace, e_dft = [], []
for r in recs:
    atoms = Atoms(symbols=r["symbols"], positions=r["positions"], calculator=calc)
    e_mace.append(atoms.get_potential_energy())
    e_dft.append(r["energy"] * 27.2114)

e_mace = np.array(e_mace)
e_dft = np.array(e_dft)

# 线性校准：用前 80% 拟合 scale/offset，后 20% 验证
n = len(e_mace)
n_tr = int(n * 0.8)
idx = np.random.RandomState(42).permutation(n)
tr, te = idx[:n_tr], idx[n_tr:]

# 拟合 DFT = a * MACE + b
A = np.vstack([e_mace[tr], np.ones(n_tr)]).T
a, b = np.linalg.lstsq(A, e_dft[tr], rcond=None)[0]

pred = a * e_mace[te] + b
mae = np.abs(pred - e_dft[te]).mean() * 1000  # meV
corr = np.corrcoef(e_mace[te], e_dft[te])[0, 1]

print(f"线性校准（训练 {n_tr}，测试 {len(te)}）", flush=True)
print(f"  scale a={a:.4f}, offset b={b:.1f} eV", flush=True)
print(f"  校准后测试 MAE = {mae:.1f} meV", flush=True)
print(f"  校准后 corr = {corr:+.4f}", flush=True)
print(f"\n{'✅ 达到化学精度！' if mae < 43 else '接近化学精度，微调可进一步改善'}", flush=True)
