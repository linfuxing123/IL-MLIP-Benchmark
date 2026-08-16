# -*- coding: utf-8 -*-
"""dft_emim_pf6.py — RDKit 构型 + PySCF 生成 [EMIM][PF6] 离子对数据。

第三个 IL（PF6 阴离子），扩充 IL 数据集。
输出：data/dft_emim_pf6.jsonl
"""
import json
import pathlib

import numpy as np

OUT = pathlib.Path(r"/mnt/d/Codex/MEC-Workspace/data/dft_emim_pf6.jsonl")

CATION_SMILES = "CC[n+]1ccn(C)c1"           # [EMIM]+
ANION_SMILES = "F[P-](F)(F)(F)(F)F"        # [PF6]-

def embed_smiles(smiles, seed):
    from rdkit import Chem
    from rdkit.Chem import AllChem
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = seed
    AllChem.EmbedMolecule(mol, params)
    conf = mol.GetConformer()
    return [a.GetSymbol() for a in mol.GetAtoms()], conf.GetPositions()

def compute_energy(symbols, positions):
    from pyscf import gto, dft
    atom = [(s, (float(p[0]), float(p[1]), float(p[2]))) for s, p in zip(symbols, positions)]
    mol = gto.M(atom=atom, basis="sto-3g", verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    return mf.kernel()

def main():
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 15
    print(f"RDKit 生成 [EMIM][PF6] 构型（{n} 个）...", flush=True)
    cat = [embed_smiles(CATION_SMILES, i) for i in range(n)]
    an = [embed_smiles(ANION_SMILES, i * 7 + 3) for i in range(n)]
    with OUT.open("w", encoding="utf-8") as f:
        for i in range(n):
            cs, cp = cat[i]
            as_, ap = an[i]
            rng = np.random.default_rng(i)
            an_dir = rng.normal(size=3); an_dir /= np.linalg.norm(an_dir)
            ap_shifted = ap + an_dir * rng.uniform(3.8, 5.5)
            symbols = cs + as_
            positions = np.vstack([cp, ap_shifted])
            try:
                e = compute_energy(symbols, positions)
            except Exception as ex:
                print(f"  [{i}] 失败: {str(ex)[:50]}", flush=True)
                continue
            rec = {"id": i, "name": "EMIM-PF6", "symbols": symbols,
                   "positions": positions.tolist(), "energy": float(e),
                   "method": "b3lyp/sto-3g", "natoms": len(symbols)}
            f.write(json.dumps(rec) + "\n"); f.flush()
            print(f"  [{i}] E={e:.4f} Ha ({len(symbols)} 原子)", flush=True)
    print(f"完成 → {OUT}", flush=True)

if __name__ == "__main__":
    main()
