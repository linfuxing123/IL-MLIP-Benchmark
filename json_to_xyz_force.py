# -*- coding: utf-8 -*-
"""json_to_xyz_force.py — Windows 读力 JSON，用 ASE write 正确 extxyz。"""
import json
import numpy as np
from ase import Atoms
import ase.io

data = json.loads(open(r"D:\Codex\MEC-Workspace\data\emim_bf4_force.json", encoding="utf-8").read())
print(f"读入 {len(data)} 帧（含能量+力）", flush=True)

atoms_list = []
for r in data:
    a = Atoms(symbols=r["symbols"], positions=r["positions"])
    # 力：Hartree/Bohr → eV/Å
    f = np.array(r["forces"]) * 27.2114 / 0.529177
    a.arrays["REF_forces"] = f
    e = r["energy"] * 27.2114  # Ha → eV
    a.info["REF_energy"] = e
    a.info["config_type"] = "Default"
    atoms_list.append(a)

out = r"D:\Codex\MEC-Workspace\data\emim_bf4_force_correct.xyz"
ase.io.write(out, atoms_list, format="extxyz")
print(f"完成 → {out}（{len(atoms_list)} 帧，ASE 正确格式）", flush=True)
