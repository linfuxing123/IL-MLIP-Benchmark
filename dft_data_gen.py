# -*- coding: utf-8 -*-
"""dft_data_gen.py — 用 PySCF 生成真实 DFT 训练数据（WSL 运行）。

工作流：
1. 选分子（H2O / CH4 / 小分子）
2. 随机采样几何（键长/角扰动）
3. PySCF DFT（B3LYP/def2-SVP 或 STO-3G 快速）算能量
4. 输出 JSONL（几何 + 能量）→ 供 ML 势训练

注意：在 WSL 里运行（pyscf 装在 Linux）。
"""
import json
import pathlib
import random

OUT = pathlib.Path(r"/mnt/d/Codex/MEC-Workspace/data/dft_h2o.jsonl")

def gen_h2o_geoms(n=50, seed=42):
    """H2O 几何采样：键长 0.90-1.05 Å，键角 100-110°。"""
    import numpy as np
    rng = np.random.default_rng(seed)
    geoms = []
    for _ in range(n):
        r = rng.uniform(0.90, 1.05)
        theta = rng.uniform(100, 110) * np.pi / 180
        o = np.array([0.0, 0.0, 0.0])
        h1 = np.array([r, 0.0, 0.0])
        h2 = np.array([r * np.cos(theta), r * np.sin(theta), 0.0])
        # 随机旋转
        from scipy.spatial.transform import Rotation as R
        rot = R.random().as_matrix()
        geoms.append({
            "symbols": ["O", "H", "H"],
            "positions": [o, h1, h2],
            "geometry": [o.tolist(), h1.tolist(), h2.tolist()],
        })
    return geoms

def compute_energy(geom):
    """PySCF DFT 单点能量（B3LYP/STO-3G 快速演示）。"""
    from pyscf import gto, dft
    atom = []
    for sym, pos in zip(geom["symbols"], geom["geometry"]):
        atom.append((sym, pos))
    mol = gto.M(atom=atom, basis="sto-3g", verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    return mf.kernel()

def main():
    geoms = gen_h2o_geoms(50)
    print(f"生成 {len(geoms)} 个 H2O 几何", flush=True)
    with OUT.open("w", encoding="utf-8") as f:
        for i, g in enumerate(geoms):
            e = compute_energy(g)
            rec = {"id": i, "symbols": g["symbols"], "positions": g["geometry"],
                   "energy": float(e), "method": "b3lyp/sto-3g"}
            f.write(json.dumps(rec) + "\n")
            if i % 10 == 0:
                print(f"  [{i}] E={e:.4f} Ha", flush=True)
    print(f"完成: {OUT}", flush=True)

if __name__ == "__main__":
    main()
