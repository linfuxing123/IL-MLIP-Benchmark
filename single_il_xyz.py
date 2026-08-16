# -*- coding: utf-8 -*-
"""single_il_xyz.py — 提取单 IL 数据（EMIM-BF4）→ XYZ，单组分微调。"""
import json
import pathlib

recs = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl", encoding="utf-8")]
# 单一 IL：EMIM-BF4（30 样本）
print(f"EMIM-BF4: {len(recs)} 样本", flush=True)

out = pathlib.Path(r"D:\Codex\MEC-Workspace\data\il_emim_bf4.xyz")
with out.open("w", encoding="utf-8") as f:
    for r in recs:
        n = len(r["symbols"])
        e_ev = r["energy"] * 27.2114
        f.write(f"{n}\n")
        f.write(f'energy={e_ev:.8f} config_type=Default name=EMIM-BF4\n')
        for s, p in zip(r["symbols"], r["positions"]):
            f.write(f"{s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}\n")
print(f"→ {out}", flush=True)
