# -*- coding: utf-8 -*-
"""check_pf6_old.py — 查 dft_il_batch.jsonl 里 EMIM-PF6 数据是否真实有效。"""
import json

pf6 = []
for line in open(r"D:\Codex\MEC-Workspace\data\dft_il_batch.jsonl", encoding="utf-8"):
    r = json.loads(line)
    if r.get("name") == "EMIM-PF6":
        pf6.append(r)

print(f"EMIM-PF6: {len(pf6)} 个")
if pf6:
    es = [r["energy"] for r in pf6]
    import numpy as np
    print(f"能量: {min(es):.4f} ~ {max(es):.4f} Ha")
    r0 = pf6[0]
    print(f"原子数: {r0['natoms']}, method: {r0.get('method')}")
    print(f"symbols 前 20: {r0['symbols'][:20]}")
    # 检查是否有力
    print(f"有力: {'forces' in r0}")
    print(f"能量样例: {es[:3]}")
