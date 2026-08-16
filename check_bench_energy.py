# -*- coding: utf-8 -*-
"""check_bench_energy.py — 检查 benchmark EMIM-BF4 能量分布 vs 之前数据。"""
import json
import numpy as np

# benchmark 数据
bench = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\il_benchmark\EMIM-BF4.jsonl", encoding="utf-8")]
es_bench = np.array([r["energy"] for r in bench])
print(f"benchmark EMIM-BF4: {len(es_bench)} 个")
print(f"  能量: {es_bench.min():.4f} ~ {es_bench.max():.4f} Ha")
print(f"  均值 {es_bench.mean():.4f}, 标准差 {es_bench.std()*1000:.1f} mHa")
# 检查异常值
q1, q3 = np.percentile(es_bench, [25, 75])
iqr = q3 - q1
outliers = es_bench[(es_bench < q1 - 1.5*iqr) | (es_bench > q3 + 1.5*iqr)]
print(f"  异常值: {len(outliers)} 个")

# 之前数据
old = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl", encoding="utf-8")]
es_old = np.array([r["energy"] for r in old])
print(f"\n之前 dft_il_rdkit: {len(es_old)} 个")
print(f"  能量: {es_old.min():.4f} ~ {es_old.max():.4f} Ha")
print(f"  均值 {es_old.mean():.4f}, 标准差 {es_old.std()*1000:.1f} mHa")
