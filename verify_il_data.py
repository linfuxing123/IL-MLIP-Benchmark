# -*- coding: utf-8 -*-
"""verify_il_data.py — 验证 IL 数据集完整性。"""
import json
import pathlib

files = [
    r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl",
    r"D:\Codex\MEC-Workspace\data\dft_bmim_ntf2.jsonl",
    r"D:\Codex\MEC-Workspace\data\dft_il_batch.jsonl",
]

all_recs = []
for p in files:
    fp = pathlib.Path(p)
    if fp.exists():
        try:
            recs = [json.loads(l) for l in fp.open(encoding="utf-8")]
            print(f"{fp.name}: {len(recs)} 条")
            all_recs.extend(recs)
        except Exception as e:
            print(f"{fp.name}: 读取错误 {e}")

# 去重检查
ids = [r.get("id") for r in all_recs]
uniq = set(ids)
print(f"\n总记录: {len(all_recs)} | 唯一 id: {len(uniq)} | 重复: {len(all_recs) - len(uniq)}")

# 各 IL 分布
from collections import Counter
names = Counter(r.get("name") for r in all_recs)
print("各 IL 分布:", dict(names))

# 能量合理性
es = [r["energy"] for r in all_recs if "energy" in r]
print(f"能量范围: {min(es):.4f} ~ {max(es):.4f} Ha")
