# -*- coding: utf-8 -*-
"""dft_bmim_ntf2.py — PySCF 生成 [BMIM][NTf2] 离子对 DFT 数据。

[BMIM]+（1-丁基-3-甲基咪唑）+ [NTf2]-（双三氟甲磺酰亚胺，常见电解质阴离子）
NTf2 含 F/N/S/O，是电解质阴离子的"金标准"。
输出：data/dft_bmim_ntf2.jsonl
"""
import json
import pathlib

import numpy as np

OUT = pathlib.Path(r"/mnt/d/Codex/MEC-Workspace/data/dft_bmim_ntf2.jsonl")

# [BMIM]+ 阳离子（C8H15N2）：咪唑环 + 丁基
BMIM_SYMBOLS = ["N", "C", "C", "N", "C", "C", "C", "C", "C", "C", "C", "C",
                "H", "H", "H", "H", "H", "H", "H", "H", "H", "H", "H", "H", "H"]
BMIM_BASE = np.array([
    # 咪唑环 N1-C2-N3-C4-C5
    [0, 0, 0.36], [-0.35, 1.1, 0], [0.35, 1.1, 0], [0.5, 0, -0.36], [-0.5, 0, -0.36],
    # 甲基（N1）+ 丁基（N3 起点）
    [0, 0, 1.85], [0.9, 1.55, 0], [1.4, 1.55, 0], [1.9, 1.05, 0], [2.4, 1.05, 0],
    # 环氢
    [-0.6, 2.0, 0], [0.6, 2.0, 0], [1.0, -0.3, -0.6], [-1.0, -0.3, -0.6],
    # 甲基氢
    [0.3, 0.5, 2.2], [-0.3, -0.5, 2.2], [0.5, -0.3, 2.0],
    # 丁基氢（近似）
    [0.4, 1.8, 0.5], [1.4, 2.0, -0.3], [1.4, 2.0, 0.3], [1.9, 1.9, -0.3],
    [1.9, 1.9, 0.3], [2.4, 1.9, -0.3], [2.4, 1.9, 0.3], [2.9, 0.8, -0.3],
    [2.9, 0.8, 0.3],
])

# [NTf2]- 阴离子（C2F6NO4S2）
NTF2_SYMBOLS = ["N", "S", "S", "O", "O", "O", "O", "C", "C", "F", "F", "F", "F", "F", "F"]
NTF2_BASE = np.array([
    [0, 0, 0], [1.6, 0, 0.6], [-1.6, 0, -0.6],
    [1.6, 1.4, 0.6], [1.6, -1.4, 0.6], [-1.6, 1.4, -0.6], [-1.6, -1.4, -0.6],
    [2.6, 0, 0.6], [-2.6, 0, -0.6],
    [3.6, 0, 0.6], [2.6, 1.0, 0.0], [2.6, -1.0, 0.0],
    [-3.6, 0, -0.6], [-2.6, 1.0, 0.0], [-2.6, -1.0, 0.0],
])

def gen_geoms(n=20, seed=11):
    rng = np.random.default_rng(seed)
    geoms = []
    for _ in range(n):
        from scipy.spatial.transform import Rotation as R
        rot_cat = R.random().as_matrix()
        cat = BMIM_BASE @ rot_cat.T
        an_dir = rng.normal(size=3)
        an_dir /= np.linalg.norm(an_dir)
        an_center = an_dir * rng.uniform(4.0, 6.0)
        an = NTF2_BASE + an_center
        symbols = BMIM_SYMBOLS + NTF2_SYMBOLS
        positions = np.vstack([cat, an])
        geoms.append({"symbols": symbols, "positions": positions.tolist()})
    return geoms

def compute_energy(symbols, geometry):
    from pyscf import gto, dft
    atom = [(s, p) for s, p in zip(symbols, geometry)]
    mol = gto.M(atom=atom, basis="sto-3g", verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    return mf.kernel()

def main():
    import sys
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    geoms = gen_geoms(n)
    print(f"生成 {len(geoms)} 个 [BMIM][NTf2] 构型（~40 原子/个）", flush=True)
    with OUT.open("w", encoding="utf-8") as f:
        for i, g in enumerate(geoms):
            e = compute_energy(g["symbols"], g["positions"])
            rec = {"id": i, "name": "BMIM-NTf2", "symbols": g["symbols"],
                   "positions": g["positions"], "energy": float(e),
                   "method": "b3lyp/sto-3g"}
            f.write(json.dumps(rec) + "\n")
            if i % 5 == 0:
                print(f"  [{i}] E={e:.4f} Ha", flush=True)
    print(f"完成: {n} 个样本 → {OUT}", flush=True)

if __name__ == "__main__":
    main()
