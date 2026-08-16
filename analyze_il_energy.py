# -*- coding: utf-8 -*-
"""analyze_il_energy.py — 分析 IL 离子对能量的涨落结构。

关键问题：离子对能量涨落（~1.6 Ha）来自什么？
假设：阴离子-阳离子距离（静电作用）主导。
验证：算能量与阴阳离子质心距离的相关性。
"""
import json

import numpy as np

p = r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl"
recs = [json.loads(l) for l in open(p, encoding="utf-8")]

# EMIM 阳离子 = 前 18 原子（C6H11N2 = 19 原子？实际 24 原子 = 阳离子 + 阴离子）
# 从 symbols 区分：阳离子含 N（咪唑）+ C/H，阴离子 BF4 含 B/F
coms_cat = []
coms_an = []
es = []
for r in recs:
    syms = r["symbols"]
    pos = np.array(r["positions"])
    cat_idx = [i for i, s in enumerate(syms) if s in ("N", "C", "H")]
    an_idx = [i for i, s in enumerate(syms) if s in ("B", "F")]
    com_cat = pos[cat_idx].mean(axis=0)
    com_an = pos[an_idx].mean(axis=0)
    coms_cat.append(com_cat)
    coms_an.append(com_an)
    es.append(r["energy"])

coms_cat = np.array(coms_cat)
coms_an = np.array(coms_an)
es = np.array(es)

# 阴阳离子质心距离
dist = np.linalg.norm(coms_cat - coms_an, axis=1)

print(f"样本数: {len(es)}")
print(f"能量: 均值 {es.mean():.4f} Ha, 标准差 {es.std()*1000:.2f} mHa")
print(f"质心距离: {dist.min():.2f} ~ {dist.max():.2f} Å")
corr = np.corrcoef(dist, es)[0, 1]
print(f"\ncorr(质心距离, 能量) = {corr:+.3f}")
print(f"→ {'静电作用主导（距离决定能量）' if abs(corr) > 0.5 else '构型复杂，非简单距离决定'}")

# 能量 vs 距离分层
print("\n距离分层能量:")
for q in [(0, 0.33), (0.33, 0.66), (0.66, 1.0)]:
    lo, hi = np.quantile(dist, q[0]), np.quantile(dist, q[1])
    mask = (dist >= lo) & (dist <= hi)
    print(f"  d∈[{lo:.2f},{hi:.2f}]: E={es[mask].mean():.4f} Ha (n={mask.sum()})")
