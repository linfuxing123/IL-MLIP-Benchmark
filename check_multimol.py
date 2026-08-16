# -*- coding: utf-8 -*-
"""check_multimol.py — 检查多分子数据。"""
import json
p = r"D:\Codex\MEC-Workspace\data\dft_multimol.jsonl"
recs = [json.loads(l) for l in open(p, encoding="utf-8")]
print("样本数:", len(recs))
names = sorted(set(r["name"] for r in recs))
print("分子:", names)
for r in recs[:4]:
    print(f"  {r['name']} E={r['energy']:.4f} Ha")
