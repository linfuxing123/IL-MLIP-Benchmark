# -*- coding: utf-8 -*-
"""more_emim_bf4.py — 补生成 EMIM-BF4 更多构型（30 → 60 样本）。

用 RDKit 新构型（不同 seed），PySCF B3LYP/STO-3G，输出追加到单 IL XYZ。
目标：单 IL 数据翻倍，让 MACE 微调验证集也达化学精度。
"""
import json
import pathlib

import numpy as np

OUT = pathlib.Path(r"/mnt/d/Codex/MEC-Workspace/data/dft_emim_bf4_more.jsonl")

CATION_SMILES = "CC[n+]1ccn(C)c1"
ANION_SMILES = "[B-](F)(F)(F)F"

def embed(smiles, seed):
    from rdkit import Chem
    from rdkit.Chem import AllChem
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    p = AllChem.ETKDGv3()
    p.randomSeed = seed
    AllChem.EmbedMolecule(mol, p)
    conf = mol.GetConformer()
    return [a.GetSymbol() for a in mol.GetAtoms()], conf.GetPositions()

def energy(symbols, positions):
    from pyscf import gto, dft
    atom = [(s, (float(x), float(y), float(z))) for s, (x, y, z) in zip(symbols, positions)]
    mol = gto.M(atom=atom, basis="sto-3g", verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    return mf.kernel()

def main():
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    print(f"补生成 {n} 个 EMIM-BF4 构型（新 seed）", flush=True)
    with OUT.open("w", encoding="utf-8") as f:
        for i in range(n):
            # 用 1000+ 的 seed（避免与已有 30 个重复）
            cs, cp = embed(CATION_SMILES, 1000 + i * 13)
            as_, ap = embed(ANION_SMILES, 1000 + i * 13 + 7)
            rng = np.random.default_rng(2000 + i)
            d = rng.normal(size=3); d /= np.linalg.norm(d)
            ap_s = ap + d * rng.uniform(3.5, 5.5)
            symbols = cs + as_
            positions = np.vstack([cp, ap_s])
            try:
                e = energy(symbols, positions)
            except Exception as ex:
                print(f"  [{i}] 失败 {str(ex)[:40]}", flush=True)
                continue
            rec = {"id": i, "name": "EMIM-BF4", "symbols": symbols,
                   "positions": positions.tolist(), "energy": float(e),
                   "method": "b3lyp/sto-3g", "natoms": len(symbols)}
            f.write(json.dumps(rec) + "\n"); f.flush()
            if i % 10 == 0:
                print(f"  [{i}] E={e:.4f} Ha", flush=True)
    print(f"完成 → {OUT}", flush=True)

if __name__ == "__main__":
    main()
