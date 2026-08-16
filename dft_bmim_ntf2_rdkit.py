# -*- coding: utf-8 -*-
"""dft_bmim_ntf2_rdkit.py — RDKit 构型 + PySCF 生成 [BMIM][NTf2] 数据。

用 RDKit ETKDG 生成合理构型（避免手工坐标问题）。
输出：data/dft_bmim_ntf2.jsonl
"""
import json
import pathlib

import numpy as np

OUT = pathlib.Path(r"/mnt/d/Codex/MEC-Workspace/data/dft_bmim_ntf2.jsonl")

CATION_SMILES = "CCCC[n+]1ccn(C)c1"           # [BMIM]+ 丁基甲基咪唑
ANION_SMILES = "O=S(=O)([N-]S(=O)(=O)C(F)(F)F)C(F)(F)F"  # [NTf2]-

def embed_smiles(smiles, seed):
    from rdkit import Chem
    from rdkit.Chem import AllChem
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = seed
    AllChem.EmbedMolecule(mol, params)
    conf = mol.GetConformer()
    symbols = [a.GetSymbol() for a in mol.GetAtoms()]
    return symbols, conf.GetPositions()

def compute_energy(symbols, positions):
    from pyscf import gto, dft
    atom = [(s, (float(p[0]), float(p[1]), float(p[2]))) for s, p in zip(symbols, positions)]
    mol = gto.M(atom=atom, basis="sto-3g", verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    return mf.kernel()

def main():
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    print(f"RDKit 生成 [BMIM][NTf2] 构型（{n} 个）...", flush=True)
    cat_geoms = [embed_smiles(CATION_SMILES, i) for i in range(n)]
    an_geoms = [embed_smiles(ANION_SMILES, i * 7 + 3) for i in range(n)]
    print("构象完成", flush=True)

    with OUT.open("w", encoding="utf-8") as f:
        for i in range(n):
            cs, cp = cat_geoms[i]
            as_, ap = an_geoms[i]
            rng = np.random.default_rng(i)
            an_dir = rng.normal(size=3)
            an_dir /= np.linalg.norm(an_dir)
            ap_shifted = ap + an_dir * rng.uniform(4.0, 6.0)
            symbols = cs + as_
            positions = np.vstack([cp, ap_shifted])
            try:
                e = compute_energy(symbols, positions)
            except Exception as ex:
                print(f"  [{i}] 失败: {str(ex)[:50]}", flush=True)
                continue
            rec = {"id": i, "name": "BMIM-NTf2", "symbols": symbols,
                   "positions": positions.tolist(), "energy": float(e),
                   "method": "b3lyp/sto-3g", "natoms": len(symbols)}
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print(f"  [{i}] E={e:.4f} Ha ({len(symbols)} 原子)", flush=True)
    print(f"完成 → {OUT}", flush=True)

if __name__ == "__main__":
    main()
