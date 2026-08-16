# -*- coding: utf-8 -*-
"""dft_il_batch.py — 批量生成 4 个 IL 离子对的 DFT 数据（规模化）。

IL 体系：EMIM-BF4、BMIM-NTf2、EMIM-PF6、BMIM-BF4
各 40 构型 = 160 样本（规模化探索数据集）
RDKit 构型 + PySCF B3LYP/STO-3G
输出：data/dft_il_batch.jsonl（增量，可断点续传）
"""
import json
import pathlib

import numpy as np

OUT = pathlib.Path(r"/mnt/d/Codex/MEC-Workspace/data/dft_il_batch.jsonl")

ILS = {
    "BMIM-NTf2": ("CCCC[n+]1ccn(C)c1", "O=S(=O)([N-]S(=O)(=O)C(F)(F)F)C(F)(F)F"),
    "EMIM-PF6": ("CC[n+]1ccn(C)c1", "F[P-](F)(F)(F)(F)F"),
    "BMIM-BF4": ("CCCC[n+]1ccn(C)c1", "[B-](F)(F)(F)F"),
}

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
    per = int(sys.argv[1]) if len(sys.argv) > 1 else 40
    # 断点续传：读已有 id
    done = set()
    if OUT.exists():
        for line in OUT.open(encoding="utf-8"):
            try:
                done.add(json.loads(line)["id"])
            except Exception:
                pass
    print(f"已续传 {len(done)} 个；目标每 IL {per} 构型", flush=True)

    i = 0
    with OUT.open("a", encoding="utf-8") as f:
        for name, (csmi, asmi) in ILS.items():
            cats = [embed(csmi, i + j) for j in range(per)]
            ans = [embed(asmi, (i + j) * 7 + 3) for j in range(per)]
            for j in range(per):
                rid = f"{name}-{j}"
                if rid in done:
                    i += 1
                    continue
                cs, cp = cats[j]
                as_, ap = ans[j]
                rng = np.random.default_rng(i)
                d = rng.normal(size=3); d /= np.linalg.norm(d)
                ap_s = ap + d * rng.uniform(3.5, 5.8)
                symbols = cs + as_
                positions = np.vstack([cp, ap_s])
                try:
                    e = energy(symbols, positions)
                except Exception as ex:
                    print(f"  [{rid}] 失败: {str(ex)[:50]}", flush=True)
                    i += 1
                    continue
                rec = {"id": rid, "name": name, "symbols": symbols,
                       "positions": positions.tolist(), "energy": float(e),
                       "method": "b3lyp/sto-3g", "natoms": len(symbols)}
                f.write(json.dumps(rec) + "\n"); f.flush()
                i += 1
                if i % 10 == 0:
                    print(f"  [{i}] {rid} E={e:.4f} Ha", flush=True)
    print(f"完成：累计 {i} 个样本 → {OUT}", flush=True)

if __name__ == "__main__":
    main()
