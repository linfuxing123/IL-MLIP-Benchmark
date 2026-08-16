# -*- coding: utf-8 -*-
"""find_bad.py — 找出 EMIM-BF4 44 个数据里的坏构型（能量偏高）。"""
import json
import numpy as np

recs = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\il_benchmark\EMIM-BF4.jsonl", encoding="utf-8")]
es = np.array([r["energy"] for r in recs])
ids = [r["id"] for r in recs]

# 排序看分布
order = np.argsort(es)
print("能量排序（从低到高）:")
for i in order:
    flag = " ⚠️坏" if es[i] > np.median(es) + 0.8 else ""
    print(f"  {ids[i]}: {es[i]:.4f} Ha{flag}")

print(f"\n中位数 {np.median(es):.4f} Ha")
print(f"正常范围参考（dft_il_rdkit）: -758.66 ~ -757.02 Ha")
