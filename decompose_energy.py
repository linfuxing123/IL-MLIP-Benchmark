# -*- coding: utf-8 -*-
"""decompose_energy.py — IL 离子对能量分解分析。

关键科学问题：离子对能量能否分解为"阳离子 + 阴离子 + 相互作用"？
若能，则 ML 势可按离子分别训练（数据需求大幅降低）。
方法：用已有数据算相互作用能 E_int = E_pair - E_cat - E_an（需单独算离子能量）。
这里先用数据分析：E_pair 与"阴阳离子距离"的依赖 → 推断相互作用能尺度。
"""
import json
import pathlib

import numpy as np

# 加载 EMIM-BF4（30 个，含阴阳离子分离构型）
recs = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl", encoding="utf-8")]

# 分阴阳离子
Z_an = {"B", "F"}
Z_cat = {"N", "C", "H"}

coms_cat, coms_an, es = [], [], []
for r in recs:
    syms = r["symbols"]
    pos = np.array(r["positions"])
    cat_idx = [i for i, s in enumerate(syms) if s in Z_cat]
    an_idx = [i for i, s in enumerate(syms) if s in Z_an]
    coms_cat.append(pos[cat_idx].mean(axis=0))
    coms_an.append(pos[an_idx].mean(axis=0))
    es.append(r["energy"])

coms_cat = np.array(coms_cat)
coms_an = np.array(coms_an)
es = np.array(es)
dist = np.linalg.norm(coms_cat - coms_an, axis=1)

print(f"EMIM-BF4 样本: {len(es)}")
print(f"能量: 均值 {es.mean():.4f} Ha, 标准差 {es.std()*1000:.1f} mHa")
print(f"质心距离: {dist.min():.2f} ~ {dist.max():.2f} Å")

# 能量 vs 距离：拟合库仑势（E_int ∝ 1/d）验证静电主导
# 若 E_pair - E_ref ∝ 1/d，则静电相互作用主导 → 可分解
d_inv = 1.0 / dist
corr_inv = np.corrcoef(d_inv, es)[0, 1]
corr_d = np.corrcoef(dist, es)[0, 1]
print(f"\ncorr(1/d, E) = {corr_inv:+.3f}")
print(f"corr(d, E) = {corr_d:+.3f}")

# 线性拟合 E = a/d + b
A = np.vstack([d_inv, np.ones_like(d_inv)]).T
a, b = np.linalg.lstsq(A, es, rcond=None)[0]
print(f"\n拟合 E = {a:.3f}/d + {b:.3f} (Ha)")
print(f"→ 库仑系数 a={a*27.2114:.1f} eV·Å（离子-离子静电 ~ 14.4 eV·Å 数量级）")

# 残差（非距离部分 = 取向等）
pred = a * d_inv + b
resid = es - pred
print(f"距离拟合残差标准差: {resid.std()*1000:.1f} mHa（非距离贡献）")
print(f"距离拟合解释方差: {1 - resid.var()/es.var():.1%}")

print("\n=== 结论 ===")
if abs(corr_inv) > 0.7:
    print("静电相互作用主导 → 离子对能量可分解为 阳离子+阴离子+库仑相互作用")
    print("→ ML 势可按组分分别训练 + 库仑项，数据需求大幅降低")
else:
    print("构型复杂，静电+取向共同主导 → 需等变模型")
