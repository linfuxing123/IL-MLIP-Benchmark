# -*- coding: utf-8 -*-
"""verify_quality.py — 验证新协议生成的数据质量。"""
import json
import numpy as np

for name in ["EMIM-BF4", "BMIM-BF4", "EMIM-NTf2"]:
    p = rf"D:\Codex\MEC-Workspace\data\il_benchmark\{name}.jsonl"
    try:
        recs = [json.loads(l) for l in open(p, encoding="utf-8")]
        es = np.array([r["energy"] for r in recs])
        if len(es) >= 3:
            print(f"{name}: {len(es)} 个, 能量 {es.min():.4f}~{es.max():.4f} Ha, std {es.std()*1000:.0f} mHa")
        else:
            print(f"{name}: {len(es)} 个（太少）")
    except FileNotFoundError:
        print(f"{name}: 文件不存在")
