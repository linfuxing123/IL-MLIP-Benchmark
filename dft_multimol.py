# -*- coding: utf-8 -*-
"""dft_multimol.py — PySCF 生成多分子 DFT 数据（电解质相关小分子）。

分子：CH4, NH3, H2O, HF（电解质体系常见组成/离子片段）
每个分子 30 几何采样 × B3LYP/STO-3G
输出：data/dft_multimol.jsonl
"""
import json
import pathlib

import numpy as np

OUT = pathlib.Path(r"/mnt/d/Codex/MEC-Workspace/data/dft_multimol.jsonl")

# 分子模板（平衡几何，后续扰动采样）
MOLECULES = {
    "CH4": {"symbols": ["C", "H", "H", "H", "H"],
            "base": np.array([[0, 0, 0], [0.63, 0.63, 0.63], [-0.63, -0.63, 0.63],
                              [0.63, -0.63, -0.63], [-0.63, 0.63, -0.63]])},
    "NH3": {"symbols": ["N", "H", "H", "H"],
            "base": np.array([[0, 0, 0.1], [0.94, 0, -0.32], [-0.47, 0.81, -0.32],
                              [-0.47, -0.81, -0.32]])},
    "H2O": {"symbols": ["O", "H", "H"],
            "base": np.array([[0, 0, 0], [0.96, 0, 0], [0.24, 0.93, 0]])},
    "HF":  {"symbols": ["F", "H"],
            "base": np.array([[0, 0, 0], [0.92, 0, 0]])},
}

def gen_geoms(name, n=30, seed=42):
    """对平衡几何加随机扰动（保持合理键长）。"""
    rng = np.random.default_rng(seed + hash(name) % 1000)
    mol = MOLECULES[name]
    base = mol["base"].astype(float)
    geoms = []
    for _ in range(n):
        # 随机旋转 + 键长缩放扰动
        from scipy.spatial.transform import Rotation as R
        rot = R.random().as_matrix()
        scale = rng.uniform(0.95, 1.05)
        pos = (base * scale) @ rot.T
        geoms.append({"symbols": mol["symbols"], "geometry": pos.tolist()})
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
    with OUT.open("w", encoding="utf-8") as f:
        i = 0
        for name in MOLECULES:
            geoms = gen_geoms(name, n)
            for g in geoms:
                e = compute_energy(g["symbols"], g["geometry"])
                rec = {"id": i, "name": name, "symbols": g["symbols"],
                       "positions": g["geometry"], "energy": float(e),
                       "method": "b3lyp/sto-3g"}
                f.write(json.dumps(rec) + "\n")
                i += 1
                if i % 20 == 0:
                    print(f"  [{i}] {name} E={e:.4f} Ha", flush=True)
    print(f"完成: {i} 个样本 → {OUT}", flush=True)

if __name__ == "__main__":
    main()
