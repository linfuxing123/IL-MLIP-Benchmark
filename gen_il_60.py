# -*- coding: utf-8 -*-
"""gen_il_60.py — 扩展到 60/IL 干净数据（8 IL = 480，接近 500）。

策略：每 IL 生成 90 个（seed 0-89），过滤坏构型（能量偏离中位数 >2 Ha），
取前 60 个干净。坏构型率 ~27%，90 → ~66 干净 → 60。
输出：data/il_benchmark_clean/{name}.jsonl（覆盖）
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
    name, (csmi, asmi), target = args
    # 生成 90 个（seed 0-89）
    all_recs = []
    for i in range(90):
        cs, cp = embed(csmi, i)
        as_, ap = embed(asmi, i * 7 + 3)
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
        all_recs.append({"id": f"{name}-{i}", "name": name, "symbols": symbols,
                         "positions": positions.tolist(), "energy": float(e),
                         "natoms": len(symbols), "method": "b3lyp/sto-3g"})
    # 过滤坏构型
    es = np.array([r["energy"] for r in all_recs])
    med = np.median(es)
    clean = [r for r in all_recs if abs(r["energy"] - med) <= 2.0]
    # 取前 target 个
    keep = clean[:target]
    out = OUT_DIR / f"{name}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for r in keep:
            f.write(json.dumps(r) + "\n")
    es_keep = np.array([r["energy"] for r in keep])
    std = es_keep.std() * 1000 if len(keep) > 1 else 0
    return name, len(all_recs), len(clean), len(keep), std

def main():
    tasks = [(name, (csmi, asmi), 60) for name, (csmi, asmi) in ILS.items()]
    print("生成 8 IL × 90 → 过滤 → 60 干净", flush=True)
    total_keep = 0
    with mp.Pool(processes=8) as pool:
        for name, n_gen, n_clean, n_keep, std in pool.imap_unordered(gen_one_il, tasks):
            total_keep += n_keep
            print(f"  {name}: 生成 {n_gen} → 干净 {n_clean} → 保留 {n_keep}（std {std:.0f} mHa）", flush=True)
    print(f"\n总干净数据: {total_keep} 个", flush=True)

if __name__ == "__main__":
    main()
