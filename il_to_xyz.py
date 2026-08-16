# -*- coding: utf-8 -*-
"""il_to_xyz.py — IL 数据转 XYZ（MACE run_train 格式）。

extended XYZ 格式：每帧含 atoms 数、注释行（含能量）、坐标。
能量单位：eV（MACE 默认）。
"""
import json
import pathlib

recs = []
for p in [r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl",
          r"D:\Codex\MEC-Workspace\data\dft_bmim_ntf2.jsonl"]:
    recs.extend([json.loads(l) for l in open(p, encoding="utf-8")])

out = pathlib.Path(r"D:\Codex\MEC-Workspace\data\il_train.xyz")
with out.open("w", encoding="utf-8") as f:
    for r in recs:
        n = len(r["symbols"])
        e_ev = r["energy"] * 27.2114  # Ha → eV
        f.write(f"{n}\n")
        f.write(f'energy={e_ev:.8f} config_type=Default name={r["name"]}\n')
        for s, p in zip(r["symbols"], r["positions"]):
            f.write(f"{s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}\n")

print(f"转换 {len(recs)} 帧 → {out}")
