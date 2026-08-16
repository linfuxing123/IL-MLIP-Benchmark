# -*- coding: utf-8 -*-
"""check_high_energy.py — 查高能构型是否原子重叠。"""
import json
import numpy as np

recs = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\il_benchmark\EMIM-BF4.jsonl", encoding="utf-8")]

def min_dist(r):
    syms = r["symbols"]
    pos = np.array(r["positions"])
    cat = [i for i, s in enumerate(syms) if s in ("N", "C", "H")]
    an = [i for i, s in enumerate(syms) if s in ("B", "F")]
    return np.linalg.norm(pos[cat][:, None, :] - pos[an][None, :, :], axis=-1).min()

# 高能构型（能量 > -757.5）
print("高能构型的最近原子距离:")
for r in recs:
    if r["energy"] > -757.5:
        d = min_dist(r)
        flag = " ⚠️重叠" if d < 1.2 else " ✓正常近距离"
        print(f"  {r['id']}: E={r['energy']:.4f} Ha, 最近距离={d:.2f} Å{flag}")

# 低能构型（正常）对比
print("\n低能构型（正常）:")
for r in recs[:3]:
    if r["energy"] < -758.5:
        d = min_dist(r)
        print(f"  {r['id']}: E={r['energy']:.4f} Ha, 最近距离={d:.2f} Å")
