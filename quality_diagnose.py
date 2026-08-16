# -*- coding: utf-8 -*-
"""quality_diagnose.py — 详细诊断 benchmark 数据质量，对比高质量基准。

目标：找出 benchmark 能量 std 937 mHa（vs 高质量 425 mHa）的来源。
"""
import json
import numpy as np

# 高质量基准（之前达化学精度 37.6 meV 的数据）
old = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl", encoding="utf-8")]
es_old = np.array([r["energy"] for r in old])
print(f"=== 高质量基准（dft_il_rdkit）===")
print(f"  30 个, 能量 {es_old.min():.4f} ~ {es_old.max():.4f} Ha")
print(f"  std {es_old.std()*1000:.1f} mHa")
# 排序看分布
sorted_old = np.sort(es_old)
print(f"  分位数: p10={np.percentile(es_old,10):.4f}, p50={np.median(es_old):.4f}, p90={np.percentile(es_old,90):.4f}")

# benchmark 数据
bench = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\il_benchmark\EMIM-BF4.jsonl", encoding="utf-8")]
es_bench = np.array([r["energy"] for r in bench])
print(f"\n=== benchmark EMIM-BF4 ===")
print(f"  {len(es_bench)} 个, 能量 {es_bench.min():.4f} ~ {es_bench.max():.4f} Ha")
print(f"  std {es_bench.std()*1000:.1f} mHa")
sorted_bench = np.sort(es_bench)
print(f"  分位数: p10={np.percentile(es_bench,10):.4f}, p50={np.median(es_bench):.4f}, p90={np.percentile(es_bench,90):.4f}")
# 找出偏离 -758 Ha 太远的（残留坏构型）
print(f"\n  偏离中位数 >2 Ha 的构型（疑似坏）:")
for r in bench:
    if abs(r["energy"] - np.median(es_bench)) > 2.0:
        print(f"    id={r['id']}, E={r['energy']:.4f} Ha")

# 关键对比：距离分布
print(f"\n=== 距离采样对比 ===")
def com_dist(r):
    syms = r["symbols"]
    pos = np.array(r["positions"])
    cat = [i for i,s in enumerate(syms) if s in ("N","C","H")]
    an = [i for i,s in enumerate(syms) if s in ("B","F")]
    return np.linalg.norm(pos[cat].mean(0) - pos[an].mean(0))
d_old = [com_dist(r) for r in old]
d_bench = [com_dist(r) for r in bench]
print(f"  基准: 距离 {min(d_old):.2f}~{max(d_old):.2f} Å")
print(f"  benchmark: 距离 {min(d_bench):.2f}~{max(d_bench):.2f} Å")
