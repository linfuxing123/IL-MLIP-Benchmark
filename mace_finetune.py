# -*- coding: utf-8 -*-
"""mace_finetune.py — MACE 预训练模型在 IL 数据上微调。

路线：
1. 加载 MACE-MP-0 预训练模型（通用材料势，已学分子间作用）
2. 在 [EMIM][BF4] 30 样本上微调（few-shot）
3. 评估能量 MAE，对比从头训练（SchNet 2178 meV）

MACE 输入：原子序数 + 位置 → 能量。ASE 集成。
"""
import json
import pathlib

import numpy as np
import torch

DATA = pathlib.Path(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl")
recs = [json.loads(l) for l in DATA.open(encoding="utf-8")]

# 原子序数映射
Z = {"H": 1, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "S": 16, "P": 15}

def to_mace_input(r):
    atomic_numbers = np.array([Z[s] for s in r["symbols"]], dtype=np.int64)
    positions = np.array(r["positions"], dtype=np.float64)
    return atomic_numbers, positions

print(f"数据: {len(recs)} 个 [EMIM][BF4] 构型", flush=True)

# MACE 训练需要 ASE atoms 格式，用 mace 的 training 脚本较重。
# 简化：直接用 MACE 预训练模型做 zero-shot 评估（先看预训练起点精度）
from mace.calculators import MACECalculator
from ase import Atoms

print("\n=== MACE-MP-0 zero-shot 评估 ===")
try:
    calc = MACECalculator(model_paths="medium", default_dtype="float64", device="cpu")
    print("MACE-MP-0 加载成功", flush=True)

    # 对前 5 个构型预测能量（与 DFT 对比）
    errs = []
    for r in recs[:5]:
        atoms = Atoms(symbols=r["symbols"], positions=r["positions"], calculator=calc)
        e_mace = atoms.get_potential_energy()  # eV
        e_dft = r["energy"] * 27.2114  # Ha → eV
        err = abs(e_mace - e_dft) * 1000  # meV
        errs.append(err)
        print(f"  [{r['id']}] MACE={e_mace:.3f} eV, DFT={e_dft:.3f} eV, |err|={err:.0f} meV", flush=True)
    print(f"\nMACE-MP-0 zero-shot 平均 |err| = {np.mean(errs):.0f} meV", flush=True)
    print(f"（对比 SchNet 从头训练 2178 meV）", flush=True)
except Exception as ex:
    print(f"MACE 加载/预测失败: {str(ex)[:200]}", flush=True)
