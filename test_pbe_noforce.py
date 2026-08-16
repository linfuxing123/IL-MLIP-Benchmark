# -*- coding: utf-8 -*-
"""test_pbe_noforce.py — 验证 PBE + 去力 能否解决 EMIM-PF6 收敛慢。"""
import time
from pyscf import gto, dft
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem

def embed(smiles, seed):
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    p = AllChem.ETKDGv3()
    p.randomSeed = seed
    AllChem.EmbedMolecule(mol, p)
    conf = mol.GetConformer()
    return [a.GetSymbol() for a in mol.GetAtoms()], conf.GetPositions()

cs, cp = embed("CC[n+]1ccn(C)c1", 12345)
as_, ap = embed("F[P-](F)(F)(F)(F)F", 12346)
rng = np.random.default_rng(42)
d = rng.normal(size=3); d /= np.linalg.norm(d)
ap_s = ap + d * 4.0  # 用较大距离 4.0Å（避免太近）
symbols = cs + as_
positions = np.vstack([cp, ap_s])
atom = [(s, (float(x), float(y), float(z))) for s, (x,y,z) in zip(symbols, positions)]
print(f"EMIM-PF6 {len(atom)} 原子")

Z = {"H":1,"B":5,"C":6,"N":7,"O":8,"F":9,"P":15,"S":16}
nelec = sum(Z[s] for s in symbols)
spin = 1 if nelec % 2 == 1 else 0
print(f"电子数 {nelec}, spin {spin}")

for label, xc, lvl in [
    ("B3LYP/STO-3G", "b3lyp", 0.0),
    ("PBE/STO-3G", "pbe", 0.0),
    ("PBE/STO-3G+level_shift", "pbe", 0.3),
]:
    mol = gto.M(atom=atom, basis="sto-3g", spin=spin, verbose=0)
    mf = dft.RKS(mol)
    mf.xc = xc
    if lvl > 0:
        mf.level_shift = lvl
    t0 = time.time()
    try:
        e = mf.kernel()
        print(f"{label}: {time.time()-t0:.1f}s, E={e:.3f}, 收敛={mf.converged}")
    except Exception as ex:
        print(f"{label}: 失败 {str(ex)[:50]}")
