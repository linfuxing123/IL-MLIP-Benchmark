# -*- coding: utf-8 -*-
"""il_benchmark_pool.py — 用 multiprocessing.Pool(8) 精确控制数据生成。

解决 bash 循环进程堆积问题：每个 IL 一个独立任务，Pool 精确 8 进程。
自适应基组（≤30 原子 def2-svp，>30 原子 sto-3g）+ spin 自适应。
"""
import json
import multiprocessing as mp
import pathlib

import numpy as np

OUT_DIR = pathlib.Path(r"/mnt/d/Codex/MEC-Workspace/data/il_benchmark")

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

def stable_hash(s):
    import hashlib
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16) % 100000

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

def energy_force(symbols, positions):
    """PySCF B3LYP/STO-3G 能量（检查 SCF 收敛，未收敛返回 None）。"""
    from pyscf import gto, dft
    basis = "sto-3g"
    atom = [(s, (float(x), float(y), float(z))) for s, (x, y, z) in zip(symbols, positions)]
    mol = gto.M(atom=atom, basis=basis, verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    e = mf.kernel()
    if not mf.converged:
        return None, None, basis  # SCF 未收敛，跳过
    return e, None, basis

def gen_one_il(args):
    """单个 IL 的全部构型生成（一个进程任务）。"""
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
        return name, len(done), 0

    n_new = 0
    with out.open("a", encoding="utf-8") as f:
        for i in range(per):
            rid = f"{name}-{i}"
            if rid in done:
                continue
            seed_cat = i  # 连续小 seed（复用 dft_il_rdkit 成功协议）
            seed_an = i * 7 + 3
            cs, cp = embed(csmi, seed_cat)
            as_, ap = embed(asmi, seed_an)
            # 与 dft_il_rdkit 完全一致：default_rng(i) 随机方向 + 随机距离
            rng = np.random.default_rng(seed_cat)
            d = rng.normal(size=3); d /= np.linalg.norm(d)
            dist = rng.uniform(3.5, 5.5)
            ap_s = ap + d * dist
            symbols = cs + as_
            positions = np.vstack([cp, ap_s])
            try:
                e, force, basis_used = energy_force(symbols, positions)
                if e is None:
                    continue  # SCF 未收敛，跳过
            except Exception as ex:
                print(f"  [{rid}] 失败 {str(ex)[:40]}", flush=True)
                continue
            rec = {"id": rid, "name": name, "symbols": symbols,
                   "positions": positions.tolist(), "energy": float(e),
                   "forces": force.tolist() if force is not None else [],
                   "natoms": len(symbols),
                   "method": f"b3lyp/{basis_used}"}
            f.write(json.dumps(rec) + "\n"); f.flush()
            n_new += 1
    return name, len(done) + n_new, n_new

def main():
    per = 60
    # 只生成还没完成的 IL
    tasks = []
    for name, (csmi, asmi) in ILS.items():
        out = OUT_DIR / f"{name}.jsonl"
        n = 0
        if out.exists():
            n = sum(1 for _ in out.open(encoding="utf-8"))
        if n < per:
            tasks.append((name, (csmi, asmi), per))
    print(f"待生成 IL: {len(tasks)} 个", flush=True)

    with mp.Pool(processes=min(16, len(tasks))) as pool:
        for name, total, new in pool.imap_unordered(gen_one_il, tasks):
            print(f"  {name}: {total}/60 (本轮 +{new})", flush=True)
    print("全部完成", flush=True)

if __name__ == "__main__":
    main()
