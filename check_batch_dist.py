# -*- coding: utf-8 -*-
"""check_batch_dist.py — 批量 IL 数据分布。"""
import json
from collections import Counter

recs = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\dft_il_batch.jsonl", encoding="utf-8")]
print("批量数据:", len(recs))
names = Counter(r["name"] for r in recs)
print("各 IL:", dict(names))
