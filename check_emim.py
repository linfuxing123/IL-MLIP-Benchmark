# -*- coding: utf-8 -*-
"""check_emim.py — 验证 EMIM-BF4 数据。"""
import json
p = r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl"
recs = [json.loads(l) for l in open(p, encoding="utf-8")]
print("样本数:", len(recs))
es = [r["energy"] for r in recs]
print(f"能量范围: {min(es):.4f} ~ {max(es):.4f} Ha")
print("原子数:", set(r["natoms"] for r in recs))
print("名称:", set(r["name"] for r in recs))
