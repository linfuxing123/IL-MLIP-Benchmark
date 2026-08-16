# -*- coding: utf-8 -*-
"""dft_il_rdkit.py — 用 RDKit 生成 IL 离子对合理 3D 坐标 → PySCF DFT。

RDKit 生成 [EMIM]+ 和 [BF4]- 的正确 3D 构型（键长/角合理），
避免手工坐标的原子重叠问题。再 PySCF B3LYP/STO-3G 算能量。
输出：data/dft_il_rdkit.jsonl
"""
import json
import pathlib

import numpy as np

OUT = pathlib.Path(r"/mnt/d/Codex/MEC-Workspace/data/dft_il_rdkit.jsonl")

# IL 离子 SMILES
CATION_SMILES = "CC[n+]1ccn(C)c1"     # [EMIM]+ 乙基甲基咪唑
ANION_SMILES = "[B-](F)(F)(F)F"       # [BF4]-

def embed_smiles(smiles, seed):
    """RDKit 生成 3D 坐标（ETKDG 构象）。"""
    from rdkit import Chem
    from rdkit.Chem import AllChem
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)
    params = AllChem.ETKDGv3()
    params.randomSeed = seed
    AllChem.EmbedMolecule(mol, params)
    conf = mol.GetConformer()
    symbols = [a.GetSymbol() for a in mol.GetAtoms()]
    positions = conf.GetPositions()
    return symbols, positions

def compute_energy(symbols, positions, charge=0):
    from pyscf import gto, dft
    atom = [(s, (float(p[0]), float(p[1]), float(p[2]))) for s, p in zip(symbols, positions)]
    mol = gto.M(atom=atom, basis="sto-3g", charge=charge, verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    return mf.kernel()

def main():
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    print(f"用 RDKit 生成 [EMIM][BF4] 构型（{n} 个）...", flush=True)

    # 预生成阳离子/阴离子构象
    cat_geoms = [embed_smiles(CATION_SMILES, i) for i in range(n)]
    an_geoms = [embed_smiles(ANION_SMILES, i * 7 + 3) for i in range(n)]
    print("RDKit 构象生成完成", flush=True)

    with OUT.open("w", encoding="utf-8") as f:
        for i in range(n):
            cs, cp = cat_geoms[i]
            as_, ap = an_geoms[i]
            # 阴离子相对阳离子随机平移（3.5-5.5 Å 分离）
            rng = np.random.default_rng(i)
            an_dir = rng.normal(size=3)
            an_dir /= np.linalg.norm(an_dir)
            an_center = an_dir * rng.uniform(3.5, 5.5)
            ap_shifted = ap + an_center
            symbols = cs + as_
            positions = np.vstack([cp, ap_shifted])
            try:
                e = compute_energy(symbols, positions, charge=0)
            except Exception as ex:
                print(f"  [{i}] 计算失败: {str(ex)[:60]}", flush=True)
                continue
            rec = {"id": i, "name": "EMIM-BF4", "symbols": symbols,
                   "positions": positions.tolist(), "energy": float(e),
                   "method": "b3lyp/sto-3g", "natoms": len(symbols)}
            f.write(json.dumps(rec) + "\n")
            f.flush()
            print(f"  [{i}] E={e:.4f} Ha ({len(symbols)} 原子)", flush=True)
    print(f"完成 → {OUT}", flush=True)

if __name__ == "__main__":
    main()
