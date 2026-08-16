# -*- coding: utf-8 -*-
"""merge_emim_60.py — 合并 30+30 EMIM-BF4 → 60 样本 XYZ。"""
import json
import pathlib

recs = []
for p in [r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl",
          r"D:\Codex\MEC-Workspace\data\dft_emim_bf4_more.jsonl"]:
    recs.extend([json.loads(l) for l in open(p, encoding="utf-8")])

# 去重（energy 近似）
seen = set()
uniq = []
for r in recs:
    key = round(r["energy"], 4)
    if key not in seen:
        seen.add(key)
        uniq.append(r)
print(f"合并 {len(recs)} → 去重后 {len(uniq)} 个 EMIM-BF4", flush=True)

out = pathlib.Path(r"D:\Codex\MEC-Workspace\data\il_emim_bf4_60.xyz")
with out.open("w", encoding="utf-8") as f:
    for r in uniq:
        n = len(r["symbols"])
        e_ev = r["energy"] * 27.2114
        f.write(f"{n}\n")
        f.write(f'energy={e_ev:.8f} config_type=Default name=EMIM-BF4\n')
        for s, p in zip(r["symbols"], r["positions"]):
            f.write(f"{s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}\n")
print(f"→ {out}（{len(uniq)} 帧）", flush=True)
