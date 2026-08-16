# -*- coding: utf-8 -*-
"""check_min_dist.py — 查高质量基准的最近原子距离分布，确定正确阈值。"""
import json
import numpy as np

def min_atom_dist(r):
    syms = r["symbols"]
    pos = np.array(r["positions"])
    cat = [i for i, s in enumerate(syms) if s in ("N", "C", "H")]
    an = [i for i, s in enumerate(syms) if s in ("B", "F", "P", "S", "O")]
    d = np.linalg.norm(pos[cat][:, None, :] - pos[an][None, :, :], axis=-1)
    return d.min()

# 高质量基准
old = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl", encoding="utf-8")]
dists = [min_atom_dist(r) for r in old]
dists = np.array(dists)
print(f"高质量基准（dft_il_rdkit 30 个）最近原子距离:")
print(f"  范围 {dists.min():.2f} ~ {dists.max():.2f} Å")
print(f"  p5={np.percentile(dists,5):.2f}, p25={np.percentile(dists,25):.2f}, p50={np.median(dists):.2f}")
print(f"  最小 {dists.min():.2f} Å（这个构型是好的，能量正常）")

# 对应能量
es = np.array([r["energy"] for r in old])
print(f"\n最近距离 {dists.min():.2f} Å 的构型能量: {es[dists.argmin()]:.4f} Ha")
print(f"能量范围: {es.min():.4f} ~ {es.max():.4f} Ha, std {es.std()*1000:.0f} mHa")
