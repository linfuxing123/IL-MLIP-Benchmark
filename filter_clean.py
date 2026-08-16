# -*- coding: utf-8 -*-
"""filter_clean.py — 过滤坏构型（能量偏离中位数 > 2 Ha）。

坏构型 = 阴阳离子重叠，能量极端偏高（偏离中位数 2-18 Ha）。
正常 IL 涨落 ~1.6 Ha，所以阈值 2 Ha 能干净分离。
"""
import json
import pathlib
import numpy as np

BENCH = pathlib.Path(r"D:\Codex\MEC-Workspace\data\il_benchmark_clean")

total_removed = 0
summary = {}
for f in BENCH.glob("*.jsonl"):
    recs = [json.loads(l) for l in f.open(encoding="utf-8")]
    if not recs:
        continue
    es = np.array([r["energy"] for r in recs])
    med = np.median(es)
    keep = [r for r in recs if abs(r["energy"] - med) <= 2.0]
    removed = len(recs) - len(keep)
    total_removed += removed
    # 重写
    with f.open("w", encoding="utf-8") as out:
        for r in keep:
            out.write(json.dumps(r) + "\n")
    es_keep = np.array([r["energy"] for r in keep])
    std = es_keep.std() * 1000 if len(es_keep) > 1 else 0
    summary[f.stem] = (len(keep), std)
    print(f"{f.stem}: {len(recs)} → {len(keep)}（移除 {removed}），std {std:.0f} mHa")

print(f"\n总移除 {total_removed} 个坏构型")
print(f"\n=== 过滤后数据 ===")
for name, (n, std) in sorted(summary.items()):
    flag = "✓" if std < 800 else "⚠️"
    print(f"  {name}: {n} 个, std {std:.0f} mHa {flag}")
