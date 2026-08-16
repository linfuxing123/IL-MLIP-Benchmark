# -*- coding: utf-8 -*-
"""mace_zero_shot.py — MACE-MP-0 正确加载 + zero-shot 评估。

用 mace_mp(model="small") 自动下载预训练权重，ASE 集成评估。
"""
import json
import pathlib

import numpy as np

DATA = pathlib.Path(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl")
recs = [json.loads(l) for l in DATA.open(encoding="utf-8")]

from mace.calculators import mace_mp
from ase import Atoms

print(f"数据: {len(recs)} 个 [EMIM][BF4]", flush=True)
print("下载 MACE-MP-0 small 模型...", flush=True)

try:
    calc = mace_mp(model="small", default_dtype="float64", device="cpu")
    print("MACE-MP-0 加载成功", flush=True)

    errs = []
    for r in recs[:8]:
        atoms = Atoms(symbols=r["symbols"], positions=r["positions"], calculator=calc)
        e_mace = atoms.get_potential_energy()  # eV
        e_dft = r["energy"] * 27.2114  # Ha → eV
        err = abs(e_mace - e_dft) * 1000  # meV
        errs.append(err)
        print(f"  [{r['id']}] MACE={e_mace:.3f} eV, DFT={e_dft:.3f} eV, |err|={err:.0f} meV", flush=True)
    print(f"\nMACE-MP-0 zero-shot 平均 |err| = {np.mean(errs):.0f} meV", flush=True)
    print(f"（对比 SchNet 从头训练 2178 meV）", flush=True)
except Exception as ex:
    print(f"失败: {str(ex)[:300]}", flush=True)
