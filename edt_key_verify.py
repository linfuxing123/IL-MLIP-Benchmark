# -*- coding: utf-8 -*-
"""edt_key_verify.py — EDT 关键验证：E_cat/E_an 涨落 vs E_pair 涨落。

若离子刚性 → E_cat/E_an 在离子对中近似常数（涨落 << E_pair 涨落 425 mHa）
→ EDT 前提成立：E_pair 涨落主要由 E_int 贡献，E_cat/E_an 只需少量数据。
"""
import json
import pathlib

import numpy as np

def calc_energy(symbols, positions, basis="sto-3g"):
    from pyscf import gto, dft
    atom = [(s, (float(x), float(y), float(z))) for s, (x,y,z) in zip(symbols, positions)]
    Z = {"H": 1, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "P": 15, "S": 16}
    nelec = sum(Z[s] for s in symbols)
    spin = 1 if nelec % 2 == 1 else 0
    mol = gto.M(atom=atom, basis=basis, spin=spin, verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    return mf.kernel()

# EMIM-BF4 数据
recs = [json.loads(l) for l in open(r"/mnt/d/Codex/MEC-Workspace/data/dft_il_rdkit.jsonl", encoding="utf-8")]
print(f"EMIM-BF4: {len(recs)} 个离子对", flush=True)

CATION_N = 19  # EMIM+ 原子数（从实际数据确定）
# 从第一个记录看符号分布
r0 = recs[0]
syms = r0["symbols"]
# 阳离子 = N,C,H（咪唑），阴离子 = B,F
cat_idx = [i for i, s in enumerate(syms) if s in ("N", "C", "H")]
an_idx = [i for i, s in enumerate(syms) if s in ("B", "F")]
print(f"阳离子 {len(cat_idx)} 原子, 阴离子 {len(an_idx)} 原子", flush=True)

# E_pair 涨落
e_pair = np.array([r["energy"] for r in recs])
print(f"\nE_pair: 均值 {e_pair.mean():.4f} Ha, 标准差 {e_pair.std()*1000:.1f} mHa", flush=True)

# 算 5 个阳离子 + 5 个阴离子孤立能量（快）
print("\n算孤立离子能量（各 5 个）...", flush=True)
e_cat, e_an = [], []
for r in recs[:5]:
    pos = np.array(r["positions"])
    cat_pos = pos[cat_idx]
    an_pos = pos[an_idx]
    cat_syms = [syms[i] for i in cat_idx]
    an_syms = [syms[i] for i in an_idx]
    e_cat.append(calc_energy(cat_syms, cat_pos))
    e_an.append(calc_energy(an_syms, an_pos))

e_cat = np.array(e_cat)
e_an = np.array(e_an)
print(f"\nE_cat(孤立 EMIM+): 均值 {e_cat.mean():.4f} Ha, 标准差 {e_cat.std()*1000:.1f} mHa", flush=True)
print(f"E_an(孤立 BF4-): 均值 {e_an.mean():.4f} Ha, 标准差 {e_an.std()*1000:.1f} mHa", flush=True)

print(f"\n=== EDT 前提验证 ===")
print(f"E_pair 涨落: {e_pair.std()*1000:.1f} mHa")
print(f"E_cat 涨落: {e_cat.std()*1000:.1f} mHa")
print(f"E_an 涨落: {e_an.std()*1000:.1f} mHa")
cat_ratio = e_cat.std() / e_pair.std() if e_pair.std() > 0 else 0
an_ratio = e_an.std() / e_pair.std() if e_pair.std() > 0 else 0
print(f"\nE_cat 涨落占 E_pair 涨落: {cat_ratio*100:.1f}%")
print(f"E_an 涨落占 E_pair 涨落: {an_ratio*100:.1f}%")
if cat_ratio < 0.1 and an_ratio < 0.1:
    print("✅ EDT 前提成立：离子能量近似常数，E_pair 涨落由 E_int 主导")
else:
    print("→ 离子能量涨落不可忽略，EDT 需分别建模")
