# -*- coding: utf-8 -*-
"""gen_il_30_clean.py — 8 IL × 30 干净数据生成（复用 dft_il_rdkit 已验证协议）。

关键：seed=i (i=0-29) 生成干净构型，不用 i>=30（会坏）。
每 IL 30 个，8 IL = 240 个干净 benchmark 数据。
输出：data/il_benchmark_clean/{name}.jsonl
"""
import json
import pathlib
import multiprocessing as mp

import numpy as np

OUT_DIR = pathlib.Path(r"/mnt/d/Codex/MEC-Workspace/data/il_benchmark_clean")
OUT_DIR.mkdir(parents=True, exist_ok=True)

ILS = {
    "EMIM-BF4": ("CC[n+]1ccn(C)c1", "[B-](F)(F)(F)F"),
    "EMIM-PF6": ("CC[n+]1ccn(C)c1", "F[P-](F)(F)(F)(F)F"),
    "EMIM-NTf2": ("CC[n+]1ccn(C)c1", "O=S(=O)([N-]S(=O)(=O)C(F)(F)F)C(F)(F)F"),
    "BMIM-BF4": ("CCCC[n+]1ccn(C)c1", "[B-](F)(F)(F)F"),
    "BMIM-NTf2": ("CCCC[n+]1ccn(C)c1", "O=S(=O)([N-]S(=O)(=O)C(F)(F)F)C(F)(F)F"),
    "BMIM-PF6": ("CCCC[n+]1ccn(C)c1", "F[P-](F)(F)(F)(F)F"),
    "Pyr14-NTf2": ("CCCC[N+]1(C)CCCC1", "O=S(=O)([N-]S(=O)(=O)C(F)(F)F)C(F)(F)F"),
    "Pyr14-FSI": ("CCCC[N+]1(C)CCCC1", "O=S(=O)([N-]S(=O)(=O)F)F"),
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
    e = mf.kernel()
    if not mf.converged:
        return None
    return e

def gen_one_il(args):
    name, (csmi, asmi), per = args
    out = OUT_DIR / f"{name}.jsonl"
    done = set()
    if out.exists():
        for line in out.open(encoding="utf-8"):
            try:
                done.add(json.loads(line)["id"])
            except Exception:
                pass
    if len(done) >= per:
        return name, len(done)

    # 复用 dft_il_rdkit 协议：seed=i (0-29)，rng=default_rng(i)
    cat_geoms = [embed(csmi, i) for i in range(per)]
    an_geoms = [embed(asmi, i * 7 + 3) for i in range(per)]
    with out.open("a", encoding="utf-8") as f:
        for i in range(per):
            rid = f"{name}-{i}"
            if rid in done:
                continue
            cs, cp = cat_geoms[i]
            as_, ap = an_geoms[i]
            rng = np.random.default_rng(i)
            an_dir = rng.normal(size=3)
            an_dir /= np.linalg.norm(an_dir)
            an_center = an_dir * rng.uniform(3.5, 5.5)
            ap_s = ap + an_center
            symbols = cs + as_
            positions = np.vstack([cp, ap_s])
            e = energy(symbols, positions)
            if e is None:
                continue
            rec = {"id": rid, "name": name, "symbols": symbols,
                   "positions": positions.tolist(), "energy": float(e),
                   "natoms": len(symbols), "method": "b3lyp/sto-3g"}
            f.write(json.dumps(rec) + "\n"); f.flush()
    return name, per

def main():
    tasks = [(name, (csmi, asmi), 30) for name, (csmi, asmi) in ILS.items()]
    print(f"生成 8 IL × 30 = 240 干净数据（dft_il_rdkit 协议）", flush=True)
    with mp.Pool(processes=8) as pool:
        for name, total in pool.imap_unordered(gen_one_il, tasks):
            print(f"  {name}: {total}/30", flush=True)
    print("全部完成", flush=True)

if __name__ == "__main__":
    main()
