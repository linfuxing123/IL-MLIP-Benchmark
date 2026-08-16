# -*- coding: utf-8 -*-
"""strict_clean.py — 严格质量过滤 + 检查最近原子距离。"""
import json
import pathlib

import numpy as np

BENCH = pathlib.Path(r"D:\Codex\MEC-Workspace\data\il_benchmark")

def min_atom_dist(r):
    """阴阳离子最近原子距离（比质心距离更严格）。"""
    syms = r["symbols"]
    pos = np.array(r["positions"])
    cat = [i for i, s in enumerate(syms) if s in ("N", "C", "H")]
    an = [i for i, s in enumerate(syms) if s in ("B", "F", "P", "S", "O")]
    # 所有阴阳离子原子对的最小距离
    d = np.linalg.norm(pos[cat][:, None, :] - pos[an][None, :, :], axis=-1)
    return d.min()

total_removed = 0
for f in BENCH.glob("*.jsonl"):
    recs = [json.loads(l) for l in f.open(encoding="utf-8")]
    if not recs:
        continue
    es = np.array([r["energy"] for r in recs])
    med = np.median(es)
    # 严格：能量偏离中位数 > 1.5 Ha（正常 IL 涨落 < 1 Ha）
    # + 最近原子距离 < 2.5 Å（离子太近 = 坏构型）
    keep = []
    for r in recs:
        ok_energy = abs(r["energy"] - med) <= 1.5
        ok_dist = min_atom_dist(r) >= 2.5
        if ok_energy and ok_dist:
            keep.append(r)
    removed = len(recs) - len(keep)
    total_removed += removed
    if removed > 0:
        with f.open("w", encoding="utf-8") as out:
            for r in keep:
                out.write(json.dumps(r) + "\n")
        es_keep = np.array([r["energy"] for r in keep])
        print(f"{f.name}: {len(recs)} → {len(keep)}（移除 {removed}，std {es_keep.std()*1000:.0f} mHa）")
    else:
        print(f"{f.name}: {len(recs)} 个，干净")

print(f"\n总移除 {total_removed} 个坏构型")
