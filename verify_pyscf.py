# -*- coding: utf-8 -*-
"""verify_pyscf.py — 验证 PySCF（WSL 内运行）。"""
from pyscf import gto, dft

mol = gto.M(atom="H 0 0 0; H 0 0 0.74", basis="sto-3g", verbose=0)
mf = dft.RKS(mol)
mf.xc = "b3lyp"
e = mf.kernel()
print(f"H2 B3LYP/STO-3G: {e:.6f} Hartree")
print("PySCF 验证通过!")
