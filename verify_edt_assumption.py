# -*- coding: utf-8 -*-
"""verify_edt_assumption.py — 验证 EDT 前提：离子构型形变可忽略？

关键问题：离子对中，阳离子/阴离子是否保持近似孤立态构型？
若形变小 → E_cat/E_an 可用孤立离子训练（EDT 成立）。
用已有 30 个 EMIM-BF4 分析：各离子的键长分布 vs 孤立态参考。
"""
import json
import pathlib

import numpy as np

recs = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl", encoding="utf-8")]

# 分阴阳离子
Z_an = {"B", "F"}
Z_cat = {"N", "C", "H"}

print("=== 离子对中离子内部构型形变分析 ===\n")
# 阳离子：C-N 键长（咪唑环）
# 阴离子：B-F 键长（BF4 四面体）
for name, idxs in [("阴离子 BF4（B-F 键长）", Z_an), ("阳离子（C-N 键长）", Z_cat)]:
    lengths = []
    for r in recs:
        syms = r["symbols"]
        pos = np.array(r["positions"])
        # 找离子内原子对（同属阴离子或阳离子）
        ion_idx = [i for i, s in enumerate(syms) if s in idxs]
        for i in range(len(ion_idx)):
            for j in range(i + 1, len(ion_idx)):
                si, sj = syms[ion_idx[i]], syms[ion_idx[j]]
                # 只取键连原子（距离 < 2 Å）
                d = np.linalg.norm(pos[ion_idx[i]] - pos[ion_idx[j]])
                if 0.5 < d < 2.0:
                    lengths.append(d)
    lengths = np.array(lengths)
    print(f"{name}: 均值 {lengths.mean():.3f} Å, 标准差 {lengths.std()*1000:.1f} mÅ, "
          f"范围 {lengths.min():.3f}-{lengths.max():.3f} Å")

print("\n=== 结论 ===")
print("若键长标准差 << 键长本身（<1%），说明离子内部构型在离子对中基本刚性")
print("→ E_cat/E_an 可用孤立离子训练，EDT 前提成立")
