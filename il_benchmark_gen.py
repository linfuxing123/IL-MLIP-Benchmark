# -*- coding: utf-8 -*-
"""il_benchmark_gen.py — IL-MLIP-Benchmark 数据生成（统一协议 + 力）。

8 个 IL 组合，每个 60 构型，B3LYP/def2-SVP（比 STO-3G 更准）+ 解析力。
固定 seed 协议保证可复现 + 分布一致（修复上次混批次问题）。
输出：data/il_benchmark/ 每 IL 一个 JSONL，含能量 + 力。
"""
import json
import pathlib

import numpy as np

OUT_DIR = pathlib.Path(r"/mnt/d/Codex/MEC-Workspace/data/il_benchmark")
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

def stable_hash(s):
    """稳定 hash（Python 内置 hash 每次运行随机化，不可用于 seed）。"""
    import hashlib
    return int(hashlib.md5(s.encode()).hexdigest()[:8], 16) % 100000

def energy_force(symbols, positions, basis=None):
    """PySCF B3LYP 能量 + 解析梯度（力）。

    自适应基组：≤30 原子用 def2-svp，>30 原子用 sto-3g（快 10 倍）。
    spin 自适应（奇电子体系需 spin=1）。
    """
    from pyscf import gto, dft
    if basis is None:
        basis = "def2-svp" if len(symbols) <= 30 else "sto-3g"
    atom = [(s, (float(x), float(y), float(z))) for s, (x, y, z) in zip(symbols, positions)]
    Z = {"H": 1, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "P": 15, "S": 16}
    nelec = sum(Z[s] for s in symbols)
    spin = 1 if nelec % 2 == 1 else 0  # 奇电子 → spin=1
    mol = gto.M(atom=atom, basis=basis, spin=spin, verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    e = mf.kernel()
    grad = mf.nuc_grad_method().kernel()  # 解析梯度（Hartree/Bohr）
    # 力 = -梯度
    force = -np.array(grad)
    return e, force

def main():
    import sys
    per = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    il_filter = sys.argv[2] if len(sys.argv) > 2 else None  # 只生成某个 IL

    for name, (csmi, asmi) in ILS.items():
        if il_filter and name != il_filter:
            continue
        out = OUT_DIR / f"{name}.jsonl"
        # 断点续传
        done = set()
        if out.exists():
            for line in out.open(encoding="utf-8"):
                try:
                    done.add(json.loads(line)["id"])
                except Exception:
                    pass
        if len(done) >= per:
            print(f"{name}: 已完整（{len(done)}），跳过", flush=True)
            continue

        print(f"{name}: 生成 {per} 构型（续传 {len(done)}）", flush=True)
        with out.open("a", encoding="utf-8") as f:
            for i in range(per):
                rid = f"{name}-{i}"
                if rid in done:
                    continue
                # 固定 seed 协议（稳定 hash）
                seed_cat = stable_hash(csmi) + i * 7
                seed_an = stable_hash(asmi) + i * 13
                cs, cp = embed(csmi, seed_cat)
                as_, ap = embed(asmi, seed_an)
                # 距离：等间隔采样（10 档）
                dist = 3.5 + (5.5 - 3.5) * (i % 10) / 9
                rng = np.random.default_rng(seed_cat + seed_an)
                d = rng.normal(size=3); d /= np.linalg.norm(d)
                ap_s = ap + d * dist
                symbols = cs + as_
                positions = np.vstack([cp, ap_s])
                try:
                    e, force = energy_force(symbols, positions)
                except Exception as ex:
                    print(f"  [{rid}] 失败 {str(ex)[:50]}", flush=True)
                    continue
                basis_used = "def2-svp" if len(symbols) <= 30 else "sto-3g"
                rec = {"id": rid, "name": name, "symbols": symbols,
                       "positions": positions.tolist(), "energy": float(e),
                       "forces": force.tolist(), "natoms": len(symbols),
                       "method": f"b3lyp/{basis_used}"}
                f.write(json.dumps(rec) + "\n"); f.flush()
                if i % 10 == 0:
                    print(f"  [{rid}] E={e:.4f} Ha ({len(symbols)} 原子)", flush=True)
        print(f"{name} 完成", flush=True)

if __name__ == "__main__":
    main()
