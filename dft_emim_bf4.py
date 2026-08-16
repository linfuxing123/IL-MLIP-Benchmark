# -*- coding: utf-8 -*-
"""dft_emim_bf4.py — PySCF 生成 [EMIM][BF4] 离子对 DFT 数据（电解质核心体系）。

[EMIM]+ 阳离子（1-乙基-3-甲基咪唑）+ [BF4]- 阴离子
30 几何采样（离子对构型） × B3LYP/STO-3G
输出：data/dft_emim_bf4.jsonl

注意：离子对 ~25 原子，STO-3G 单点较慢（分钟级），30 个约需 30-60 分钟。
"""
import json
import pathlib

import numpy as np

OUT = pathlib.Path(r"/mnt/d/Codex/MEC-Workspace/data/dft_emim_bf4.jsonl")

# [EMIM]+ 阳离子（C6H11N2）平衡几何近似
EMIM_SYMBOLS = ["N", "C", "C", "N", "C", "C", "C", "C", "C", "C", "C", "C",
                "C", "H", "H", "H", "H", "H", "H", "H", "H", "H", "H", "H", "H"]
EMIM_BASE = np.array([
    # 咪唑环（N1-C2-N3-C4-C5）
    [0, 0, 0.36], [-0.35, 1.1, 0], [0.35, 1.1, 0], [0.5, 0, -0.36], [-0.5, 0, -0.36],
    # 甲基（N1 上）和乙基（N3 上）
    [0, 0, 1.85], [0.9, 1.55, 0], [0.9, 2.05, 0],
    # 环上氢
    [-0.6, 2.0, 0], [0.6, 2.0, 0], [1.0, -0.3, -0.6], [-1.0, -0.3, -0.6],
    # 甲基氢
    [0.3, 0.5, 2.2], [-0.3, -0.5, 2.2], [0.5, -0.3, 2.0],
    # 乙基氢
    [1.3, 1.3, 0.5], [0.4, 1.6, 0.5], [1.3, 2.5, -0.3], [1.3, 2.5, 0.3],
    [1.0, 2.5, 0.5], [0.4, 2.5, 0.5],
    # 补充环碳氢
    [-0.9, 1.5, 0], [0.9, 1.5, 0], [1.5, 0, -0.6],
])

# [BF4]- 阴离子
BF4_SYMBOLS = ["B", "F", "F", "F", "F"]
BF4_BASE = np.array([[0, 0, 0], [1.0, 1.0, 1.0], [-1.0, -1.0, 1.0],
                     [1.0, -1.0, -1.0], [-1.0, 1.0, -1.0]])

def gen_geoms(n=30, seed=7):
    rng = np.random.default_rng(seed)
    geoms = []
    for _ in range(n):
        # 阴离子相对阳离子的随机位置（3.5-5.5 Å 分离）
        from scipy.spatial.transform import Rotation as R
        rot_cat = R.random().as_matrix()
        cat = EMIM_BASE @ rot_cat.T
        an_dir = rng.normal(size=3)
        an_dir /= np.linalg.norm(an_dir)
        an_center = an_dir * rng.uniform(3.5, 5.5)
        an = BF4_BASE + an_center
        symbols = EMIM_SYMBOLS + BF4_SYMBOLS
        positions = np.vstack([cat, an])
        geoms.append({"symbols": symbols, "positions": positions.tolist(),
                      "charge": 0})
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
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    geoms = gen_geoms(n)
    print(f"生成 {len(geoms)} 个 [EMIM][BF4] 构型（约 {len(EMIM_SYMBOLS)} 原子/个）", flush=True)
    with OUT.open("w", encoding="utf-8") as f:
        for i, g in enumerate(geoms):
            e = compute_energy(g["symbols"], g["positions"])
            rec = {"id": i, "name": "EMIM-BF4", "symbols": g["symbols"],
                   "positions": g["positions"], "energy": float(e),
                   "method": "b3lyp/sto-3g"}
            f.write(json.dumps(rec) + "\n")
            if i % 5 == 0:
                print(f"  [{i}] E={e:.4f} Ha", flush=True)
    print(f"完成: {n} 个样本 → {OUT}", flush=True)

if __name__ == "__main__":
    main()
