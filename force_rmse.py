# -*- coding: utf-8 -*-
"""force_rmse.py — 补算 PySCF 力 + MACE 力预测，算力 RMSE。

EMIM-BF4 24 原子（力计算快）。流程：
1. PySCF nuc_grad 算参考力（10 个构型）
2. MACE 微调模型算力（autograd）
3. 力 RMSE（meV/Å）
"""
import json
import pathlib
import numpy as np

from mace.calculators import MACECalculator
from ase import Atoms

# 用已微调的 MACE 模型（之前 bench_clean 训练的）
MODEL = r"D:\Codex\MEC-Workspace\data\mace_bench_q\bench_q.model"  # 可能不存在，用下面的

def pyscf_force(symbols, positions):
    """PySCF 解析梯度（力 = -梯度）。"""
    from pyscf import gto, dft
    atom = [(s, (float(x), float(y), float(z))) for s, (x, y, z) in zip(symbols, positions)]
    mol = gto.M(atom=atom, basis="sto-3g", verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    mf.kernel()
    grad = mf.nuc_grad_method().kernel()
    return -np.array(grad)  # 力 = -梯度（Hartree/Bohr）

def main():
    recs = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\il_benchmark_clean\EMIM-BF4.jsonl", encoding="utf-8")]
    # 取前 10 个算力
    print(f"算 {min(10, len(recs))} 个构型的力（PySCF nuc_grad）...", flush=True)
    force_refs = []
    for r in recs[:10]:
        f = pyscf_force(r["symbols"], r["positions"])
        force_refs.append(f * 27.2114 / 0.529177)  # Hartree/Bohr → eV/Å
    force_refs = np.array(force_refs)
    print(f"PySCF 力: 形状 {force_refs.shape}, 范围 {force_refs.min():.2f}~{force_refs.max():.2f} eV/Å", flush=True)

    # MACE 力预测（用 MACE-MP-0 预训练，先看 zero-shot 力）
    calc = MACECalculator(model_paths=r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model",
                          default_dtype="float64", device="cuda")
    force_preds = []
    for r in recs[:10]:
        atoms = Atoms(symbols=r["symbols"], positions=r["positions"], calculator=calc)
        f = atoms.get_forces()  # eV/Å
        force_preds.append(f)
    force_preds = np.array(force_preds)
    print(f"MACE 力: 形状 {force_preds.shape}", flush=True)

    # 力 RMSE
    diff = force_preds - force_refs
    rmse = np.sqrt((diff**2).mean()) * 1000  # meV/Å
    mae = np.abs(diff).mean() * 1000
    print(f"\n力 RMSE = {rmse:.0f} meV/Å, MAE = {mae:.0f} meV/Å", flush=True)
    print(f"（参考：力 RMSE < 50 meV/Å 通常视为合格）", flush=True)

if __name__ == "__main__":
    main()
