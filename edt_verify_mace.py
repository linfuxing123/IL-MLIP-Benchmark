# -*- coding: utf-8 -*-
"""edt_verify_mace.py — 用 MACE 快速验证 EDT 核心主张。

EDT: E_pair = E_cat + E_an + E_int
关键验证：E_int 的涨落是否 < E_pair 的涨落（决定 EDT 是否降低拟合难度）。

用 MACE（GPU）快速算孤立离子 + 离子对能量，比较涨落。
"""
import json
import numpy as np

from mace.calculators import MACECalculator
from ase import Atoms

MODEL = r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model"
calc = MACECalculator(model_paths=MODEL, default_dtype="float64", device="cuda")

# 用 EMIM-BF4 数据（dft_il_rdkit 30 个，高质量）
recs = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl", encoding="utf-8")]
print(f"EMIM-BF4 {len(recs)} 个离子对", flush=True)

CATION_N = 19  # EMIM+ 原子数
ANION_N = 5    # BF4- 原子数

def mace_energy(symbols, positions):
    atoms = Atoms(symbols=symbols, positions=positions, calculator=calc)
    return atoms.get_potential_energy()  # eV

e_pair, e_cat, e_an = [], [], []
for r in recs[:20]:
    pos = np.array(r["positions"])
    syms = r["symbols"]
    # 离子对
    e_pair.append(mace_energy(syms, pos))
    # 阳离子孤立
    cat_syms = syms[:CATION_N]
    cat_pos = pos[:CATION_N]
    e_cat.append(mace_energy(cat_syms, cat_pos))
    # 阴离子孤立
    an_syms = syms[CATION_N:]
    an_pos = pos[CATION_N:]
    e_an.append(mace_energy(an_syms, an_pos))

e_pair = np.array(e_pair)
e_cat = np.array(e_cat)
e_an = np.array(e_an)
e_int = e_pair - e_cat - e_an  # 相互作用能

print(f"\n=== EDT 涨落分解（MACE 能量，20 个离子对）===", flush=True)
print(f"E_pair: std {e_pair.std()*1000:.0f} meV", flush=True)
print(f"E_cat:  std {e_cat.std()*1000:.0f} meV（离子刚性 → 应很小）", flush=True)
print(f"E_an:   std {e_an.std()*1000:.0f} meV（离子刚性 → 应很小）", flush=True)
print(f"E_int:  std {e_int.std()*1000:.0f} meV", flush=True)

ratio = e_int.std() / e_pair.std() if e_pair.std() > 0 else 0
print(f"\nE_int/E_pair 涨落比 = {ratio:.2f}", flush=True)
if ratio < 0.8:
    print(f"✅ EDT 价值成立：E_int 涨落比 E_pair 小 {(1-ratio)*100:.0f}%，拟合 E_int 更容易", flush=True)
else:
    print(f"→ E_int 涨落 ≈ E_pair（EDT 不降低拟合难度，但提供可迁移性）", flush=True)
