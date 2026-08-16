# -*- coding: utf-8 -*-
"""prof_df t.py — 剖析 PySCF DFT 单点的耗时分布（WSL）。"""
import time
from pyscf import gto, dft

# EMIM-BF4 24 原子 vs BMIM-NTf2 40 原子，看 SCF vs 梯度 vs 积分耗时
for label, atom, basis in [
    ("EMIM-BF4(24原子)", "C 0 0 0; C 1.4 0 0; N 2.8 0 0; C 4.2 0 0; N 5.6 0 0; H 0 -1 0; H 1.4 1 0; H 4.2 1 0; B 8 0 0; F 9 0 0; F 7.5 0.8 0; F 8 0 0.8", "def2-svp"),
    ("BMIM-NTf2(40原子)", "C 0 0 0; C 1.4 0 0; N 2.8 0 0; S 4.2 0 0; O 4.2 1.2 0; O 4.2 -1.2 0; F 5.6 0 0; C 7 0 0; F 7 1 0; F 7 -1 0; F 8.4 0 0", "def2-svp"),
]:
    mol = gto.M(atom=atom, basis=basis, verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    t0 = time.time()
    e = mf.kernel()
    t_scf = time.time() - t0
    t0 = time.time()
    g = mf.nuc_grad_method().kernel()
    t_grad = time.time() - t0
    print(f"{label}: SCF {t_scf:.1f}s + 梯度 {t_grad:.1f}s = {t_scf+t_grad:.1f}s", flush=True)
