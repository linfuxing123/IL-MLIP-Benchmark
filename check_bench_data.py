# -*- coding: utf-8 -*-
"""check_bench_data.py — 验证 benchmark 数据质量。"""
import json

for f in ["BMIM-NTf2", "BMIM-PF6", "EMIM-BF4", "Pyr14-FSI"]:
    p = rf"D:\Codex\MEC-Workspace\data\il_benchmark\{f}.jsonl"
    try:
        recs = [json.loads(l) for l in open(p, encoding="utf-8")]
        if recs:
            r = recs[0]
            has_force = len(r.get("forces", [])) > 0
            print(f"{f}: {len(recs)} 样本, {r['natoms']} 原子, method={r['method']}, 力={has_force}")
        else:
            print(f"{f}: 0 样本")
    except FileNotFoundError:
        print(f"{f}: 文件不存在")
    except Exception as e:
        print(f"{f}: {e}")
