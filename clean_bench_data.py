# -*- coding: utf-8 -*-
"""clean_bench_data.py — 清理 benchmark 数据的异常能量（SCF 未收敛的坏构型）。

方法：按 IL 分组，过滤能量偏离中位数 5 个 MAD（中位绝对偏差）的异常值。
"""
import json
import pathlib

import numpy as np

BENCH = pathlib.Path(r"D:\Codex\MEC-Workspace\data\il_benchmark")

for f in BENCH.glob("*.jsonl"):
    recs = [json.loads(l) for l in f.open(encoding="utf-8")]
    if not recs:
        continue
    es = np.array([r["energy"] for r in recs])
    med = np.median(es)
    mad = np.median(np.abs(es - med))
    # 阈值：偏离中位数 5 个 MAD（稳健异常检测）
    thresh = 5 * (mad if mad > 0 else 1e-6)
    keep = [r for r in recs if abs(r["energy"] - med) <= thresh]
    removed = len(recs) - len(keep)
    if removed > 0:
        # 重写（保留正常数据）
        with f.open("w", encoding="utf-8") as out:
            for r in keep:
                out.write(json.dumps(r) + "\n")
        print(f"{f.name}: {len(recs)} → {len(keep)}（移除 {removed} 个异常，能量范围 {med-thresh:.2f}~{med+thresh:.2f} Ha）")
    else:
        print(f"{f.name}: {len(recs)} 个，无异常")
