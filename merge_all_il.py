# -*- coding: utf-8 -*-
"""merge_all_il.py — 合并所有 IL 数据 → XYZ（4 IL 体系）。"""
import json
import pathlib

recs = []
files = [
    r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl",       # EMIM-BF4 30
    r"D:\Codex\MEC-Workspace\data\dft_bmim_ntf2.jsonl",      # BMIM-NTf2 15
    r"D:\Codex\MEC-Workspace\data\dft_il_batch.jsonl",       # 107
]
for p in files:
    fp = pathlib.Path(p)
    if fp.exists():
        recs.extend([json.loads(l) for l in fp.open(encoding="utf-8")])

# 去重（按 name + energy 近似）
seen = set()
uniq = []
for r in recs:
    key = (r["name"], round(r["energy"], 6))
    if key not in seen:
        seen.add(key)
        uniq.append(r)
print(f"合并 {len(recs)} → 去重后 {len(uniq)} 个 IL 离子对", flush=True)

from collections import Counter
print("分布:", dict(Counter(r["name"] for r in uniq)), flush=True)

out = pathlib.Path(r"D:\Codex\MEC-Workspace\data\il_all.xyz")
with out.open("w", encoding="utf-8") as f:
    for r in uniq:
        n = len(r["symbols"])
        e_ev = r["energy"] * 27.2114
        f.write(f"{n}\n")
        f.write(f'energy={e_ev:.8f} config_type=Default name={r["name"]}\n')
        for s, p in zip(r["symbols"], r["positions"]):
            f.write(f"{s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}\n")
print(f"→ {out}（{len(uniq)} 帧）", flush=True)
