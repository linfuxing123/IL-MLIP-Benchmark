# -*- coding: utf-8 -*-
"""mace_eval_local.py — 用下载好的 MACE 权重跑 zero-shot 评估。"""
import json
import pathlib

import numpy as np

DATA = pathlib.Path(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl")
MODEL = r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model"
recs = [json.loads(l) for l in DATA.open(encoding="utf-8")]

from mace.calculators import MACECalculator
from ase import Atoms

print(f"数据: {len(recs)} 个 [EMIM][BF4]", flush=True)
print(f"MACE 权重: {MODEL}", flush=True)

try:
    calc = MACECalculator(model_paths=MODEL, default_dtype="float64", device="cpu")
    print("MACE-MP-0 加载成功", flush=True)

    errs = []
    for r in recs[:10]:
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
