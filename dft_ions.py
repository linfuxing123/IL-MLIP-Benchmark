# -*- coding: utf-8 -*-
"""dft_ions.py — PySCF 生成电解质离子片段 DFT 数据。

离子：BF4-、PF6-、NO3-、NH4+（电解质常见阴/阳离子片段）
每个 20 几何采样 × B3LYP/STO-3G
输出：data/dft_ions.jsonl
"""
import json
import pathlib

import numpy as np

OUT = pathlib.Path(r"/mnt/d/Codex/MEC-Workspace/data/dft_ions.jsonl")

# 离子平衡几何（STO-3G 合理初值）
IONS = {
    "BF4": {"symbols": ["B", "F", "F", "F", "F"], "charge": -1,
            "base": np.array([[0, 0, 0], [0.71, 0.71, 0.71], [-0.71, -0.71, 0.71],
                              [0.71, -0.71, -0.71], [-0.71, 0.71, -0.71]])},
    "PF6": {"symbols": ["P", "F", "F", "F", "F", "F", "F"], "charge": -1,
            "base": np.array([[0, 0, 0], [1.6, 0, 0], [-1.6, 0, 0], [0, 1.6, 0],
                              [0, -1.6, 0], [0, 0, 1.6], [0, 0, -1.6]])},
    "NO3": {"symbols": ["N", "O", "O", "O"], "charge": -1,
            "base": np.array([[0, 0, 0], [1.25, 0, 0], [-0.62, 1.08, 0], [-0.62, -1.08, 0]])},
    "NH4": {"symbols": ["N", "H", "H", "H", "H"], "charge": 1,
            "base": np.array([[0, 0, 0], [0.63, 0.63, 0.63], [-0.63, -0.63, 0.63],
                              [0.63, -0.63, -0.63], [-0.63, 0.63, -0.63]])},
}

def gen_geoms(name, n=20, seed=123):
    rng = np.random.default_rng(seed + hash(name) % 997)
    ion = IONS[name]
    base = ion["base"].astype(float)
    geoms = []
    for _ in range(n):
        from scipy.spatial.transform import Rotation as R
        rot = R.random().as_matrix()
        scale = rng.uniform(0.97, 1.03)
        pos = (base * scale) @ rot.T
        geoms.append({"symbols": ion["symbols"], "charge": ion["charge"],
                      "geometry": pos.tolist()})
    return geoms

def compute_energy(symbols, geometry, charge):
    from pyscf import gto, dft
    atom = [(s, p) for s, p in zip(symbols, geometry)]
    mol = gto.M(atom=atom, basis="sto-3g", charge=charge, verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    return mf.kernel()

def main():
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    with OUT.open("w", encoding="utf-8") as f:
        i = 0
        for name in IONS:
            geoms = gen_geoms(name, n)
            for g in geoms:
                e = compute_energy(g["symbols"], g["geometry"], g["charge"])
                rec = {"id": i, "name": name, "symbols": g["symbols"],
                       "charge": g["charge"], "positions": g["geometry"],
                       "energy": float(e), "method": "b3lyp/sto-3g"}
                f.write(json.dumps(rec) + "\n")
                i += 1
                if i % 15 == 0:
                    print(f"  [{i}] {name} E={e:.4f} Ha", flush=True)
    print(f"完成: {i} 个样本 → {OUT}", flush=True)

if __name__ == "__main__":
    main()
