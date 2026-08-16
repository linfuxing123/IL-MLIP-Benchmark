# -*- coding: utf-8 -*-
"""clean_bench.py — 干净诊断：能量 vs 能量+力 的耗时。"""
import time
from pyscf import gto, dft

# 用真实 EMIM-BF4 几何（从已有数据取一个）
import json
recs = [json.loads(l) for l in open(r"/mnt/d/Codex/MEC-Workspace/data/dft_il_rdkit.jsonl", encoding="utf-8")]
r = recs[0]
atom = [(s, tuple(p)) for s, p in zip(r["symbols"], r["positions"])]
print(f"EMIM-BF4 {len(atom)} 原子")

for basis in ["sto-3g", "def2-svp"]:
    mol = gto.M(atom=atom, basis=basis, verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    t0 = time.time()
    e = mf.kernel()
    t_scf = time.time() - t0
    print(f"\n{basis}: SCF(能量) = {t_scf:.1f}s, E={e:.3f} Ha")
    # 力计算
    t0 = time.time()
    g = mf.nuc_grad_method().kernel()
    t_grad = time.time() - t0
    print(f"  {basis}: 梯度(力) = {t_grad:.1f}s  → 力是能量的 {t_grad/max(t_scf,0.1):.1f} 倍耗时")
