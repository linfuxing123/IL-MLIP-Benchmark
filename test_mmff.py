# -*- coding: utf-8 -*-
"""test_mmff.py — 验证 MMFF 优化能否消除原子重叠坏构型。

昨天发现 RDKit ETKDG 某些 seed 生成阴阳离子重叠（坏构型）。
验证：embed 后加 MMFF 力场优化，看最近原子距离是否都 > 1.5 Å（无重叠）。
"""
import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem

def embed_and_opt(smiles, seed, opt=True):
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    p = AllChem.ETKDGv3()
    p.randomSeed = seed
    AllChem.EmbedMolecule(mol, p)
    if opt:
        # MMFF 力场优化（消除重叠）
        AllChem.MMFFOptimizeMolecule(mol, maxIters=200)
    conf = mol.GetConformer()
    return [a.GetSymbol() for a in mol.GetAtoms()], conf.GetPositions()

CATION = "CC[n+]1ccn(C)c1"   # EMIM+
ANION = "[B-](F)(F)(F)F"      # BF4-

print("=== EMIM-BF4 阴阳离子最近原子距离（seed 0-59）===")
bad_count = {"no_opt": 0, "opt": 0}
for i in range(60):
    # 阴阳离子分别 embed（不优化，模拟昨天的问题）
    cs, cp = embed_and_opt(CATION, i, opt=False)
    as_, ap = embed_and_opt(ANION, i*7+3, opt=False)
    rng = np.random.default_rng(i)
    d = rng.normal(size=3); d /= np.linalg.norm(d)
    dist = rng.uniform(3.5, 5.5)
    ap_s = ap + d * dist
    cand = np.vstack([cp, ap_s])
    min_d = np.linalg.norm(cand[:len(cs)][:,None,:] - cand[len(cs):][None,:,:], axis=-1).min()
    if min_d < 1.2:
        bad_count["no_opt"] += 1
        # 看 MMFF 优化离子本身能否改善
        cs2, cp2 = embed_and_opt(CATION, i, opt=True)
        as2, ap2 = embed_and_opt(ANION, i*7+3, opt=True)
        cand2 = np.vstack([cp2, ap2 + d*dist])
        min_d2 = np.linalg.norm(cand2[:len(cs2)][:,None,:] - cand2[len(cs2):][None,:,:], axis=-1).min()
        if min_d2 < 1.2:
            bad_count["opt"] += 1

print(f"未优化坏构型（min_d<1.2Å）: {bad_count['no_opt']}/60")
print(f"MMFF 优化后仍坏: {bad_count['opt']}/{bad_count['no_opt']}")
print(f"\n→ {'MMFF 优化有效消除重叠' if bad_count['opt'] < bad_count['no_opt'] else 'MMFF 优化离子本身不够（重叠来自相对位置，需优化离子对）'}")
