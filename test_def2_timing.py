# -*- coding: utf-8 -*-
"""test_def2_timing.py — 测 def2-SVP vs STO-3G 耗时（WSL）。"""
import time
from pyscf import gto, dft

# 4 原子小分子测耗时（偶数电子）
for basis in ["sto-3g", "def2-svp"]:
    mol = gto.M(atom="C 0 0 0; O 0 0 1.2; H 1.0 0 1.6; H -1.0 0 1.6", basis=basis, verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    t0 = time.time()
    e = mf.kernel()
    t1 = time.time()
    print(f"{basis}: {t1-t0:.2f}s, E={e:.4f} Ha")
