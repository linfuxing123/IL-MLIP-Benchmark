# -*- coding: utf-8 -*-
"""verify_edt2.py — 用 RDKit 判断真实化学键，重新分析离子形变。"""
import json
import pathlib

import numpy as np
from rdkit import Chem

recs = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl", encoding="utf-8")]

CATION_SMILES = "CC[n+]1ccn(C)c1"
ANION_SMILES = "[B-](F)(F)(F)F"

# RDKit 分子 + 键信息
def get_bonds(smiles):
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    bonds = [(b.GetBeginAtomIdx(), b.GetEndAtomIdx()) for b in mol.GetBonds()]
    return bonds

cat_bonds = get_bonds(CATION_SMILES)
an_bonds = get_bonds(ANION_SMILES)

# 阴阳离子原子数
cat_n = len([a for a in Chem.AddHs(Chem.MolFromSmiles(CATION_SMILES)).GetAtoms()])
an_n = len([a for a in Chem.AddHs(Chem.MolFromSmiles(ANION_SMILES)).GetAtoms()])

print(f"阳离子 {cat_n} 原子 {len(cat_bonds)} 键 | 阴离子 {an_n} 原子 {len(an_bonds)} 键\n")

def analyze(name, bonds, offset, symbols_slice):
    bond_lengths = {i: [] for i in range(len(bonds))}
    for r in recs:
        pos = np.array(r["positions"])
        sub = pos[offset:offset+len(symbols_slice)] if offset else pos[:len(symbols_slice)]
        for bi, (a, b) in enumerate(bonds):
            d = np.linalg.norm(sub[a] - sub[b])
            bond_lengths[bi].append(d)
    print(f"{name}:")
    for bi in range(len(bonds)):
        arr = np.array(bond_lengths[bi])
        print(f"  键 {bi}: 均值 {arr.mean():.3f} Å, 标准差 {arr.std()*1000:.1f} mÅ")
    all_std = np.mean([np.std(np.array(bond_lengths[bi])) for bi in range(len(bonds))])
    print(f"  → 平均键长标准差 {all_std*1000:.1f} mÅ")
    return all_std

# 阳离子（前 cat_n 原子）
cat_syms = [r["symbols"][:cat_n] for r in recs]
std_cat = analyze("阳离子 EMIM+", cat_bonds, 0, cat_syms[0])
# 阴离子（后 an_n 原子）
an_syms = [r["symbols"][cat_n:] for r in recs]
std_an = analyze("阴离子 BF4-", an_bonds, cat_n, an_syms[0])

print(f"\n=== 结论 ===")
print(f"阴离子形变 {std_an*1000:.1f} mÅ, 阳离子形变 {std_cat*1000:.1f} mÅ")
if std_an*1000 < 50 and std_cat*1000 < 100:
    print("→ 离子在离子对中近似刚性，EDT 前提成立 ✅")
else:
    print("→ 形变不可忽略，EDT 需考虑极化修正")
