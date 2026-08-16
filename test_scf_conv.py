# -*- coding: utf-8 -*-
"""test_scf_conv.py — 测卡住 IL 的 SCF 收敛（加 level_shift 对比）。"""
import time
from pyscf import gto, dft
import numpy as np

# 用 EMIM-PF6 的第一个构型（卡住的 IL）
# 构造 EMIM-PF6：EMIM+ (19原子) + PF6- (7原子)
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
# 距离采样
rng = np.random.default_rng(12345+12346)
d = rng.normal(size=3); d /= np.linalg.norm(d)
ap_s = ap + d * 3.5
symbols = cs + as_
positions = np.vstack([cp, ap_s])
atom = [(s, (float(x), float(y), float(z))) for s, (x,y,z) in zip(symbols, positions)]
print(f"EMIM-PF6 {len(atom)} 原子")

for label, kwargs in [
    ("默认", {}),
    ("level_shift=0.3", {"level_shift": 0.3}),
    ("diis_space=10", {"diis_space": 10}),
]:
    mol = gto.M(atom=atom, basis="sto-3g", verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    for k, v in kwargs.items():
        setattr(mf, k, v)
    t0 = time.time()
    try:
        e = mf.kernel()
        conv = mf.converged
        print(f"{label}: {time.time()-t0:.1f}s, E={e:.3f}, 收敛={conv}")
    except Exception as ex:
        print(f"{label}: 失败 {str(ex)[:50]}")
