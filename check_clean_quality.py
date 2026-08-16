# -*- coding: utf-8 -*-
"""check_clean_quality.py — 验证 clean 数据质量（std 应 ~400-500 mHa，无坏构型）。"""
import json
import numpy as np

for name in ["EMIM-BF4", "BMIM-BF4", "EMIM-NTf2", "Pyr14-FSI"]:
    p = rf"D:\Codex\MEC-Workspace\data\il_benchmark_clean\{name}.jsonl"
    try:
        recs = [json.loads(l) for l in open(p, encoding="utf-8")]
        es = np.array([r["energy"] for r in recs])
        if len(es) >= 5:
            print(f"{name}: {len(es)} 个, std {es.std()*1000:.0f} mHa, 范围 {es.max()-es.min():.2f} Ha")
    except FileNotFoundError:
        pass
