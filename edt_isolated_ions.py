# -*- coding: utf-8 -*-
"""edt_isolated_ions.py — 生成孤立离子能量（EDT 的 E_cat/E_an）。

关键：从已有离子对数据提取阳离子/阴离子坐标，算孤立能量。
EDT: E_int = E_pair - E_cat(孤立) - E_an(孤立)

先用已有 165 个 IL 数据里的离子坐标，算孤立能量（快，单离子）。
"""
import json
import pathlib

import numpy as np

# IL 组成定义
ILS = {
    "EMIM-BF4": {"cat": ("CC[n+]1ccn(C)c1", 19), "an": ("[B-](F)(F)(F)F", 5)},
    "BMIM-NTf2": {"cat": ("CCCC[n+]1ccn(C)c1", 23), "an": ("O=S(=O)([N-]S(=O)(=O)C(F)(F)F)C(F)(F)F", 15)},
    "EMIM-PF6": {"cat": ("CC[n+]1ccn(C)c1", 19), "an": ("F[P-](F)(F)(F)(F)F", 7)},
    "BMIM-BF4": {"cat": ("CCCC[n+]1ccn(C)c1", 23), "an": ("[B-](F)(F)(F)F", 5)},
}

def load_pairs():
    """加载所有已有离子对数据（按 IL 分组）。"""
    files = [
        r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl",
        r"D:\Codex\MEC-Workspace\data\dft_bmim_ntf2.jsonl",
        r"D:\Codex\MEC-Workspace\data\dft_il_batch.jsonl",
    ]
    pairs = {}
    for f in files:
        p = pathlib.Path(f)
        if not p.exists():
            continue
        for line in p.open(encoding="utf-8"):
            r = json.loads(line)
            name = r.get("name")
            if name in ILS:
                pairs.setdefault(name, []).append(r)
    return pairs

def main():
    pairs = load_pairs()
    print("=== 已有离子对数据（EDT 可复用）===")
    for name, recs in pairs.items():
        print(f"  {name}: {len(recs)} 个离子对")

    # 关键洞察：每个离子对里的阳离子/阴离子坐标是现成的
    # EDT 只需补算"孤立离子能量"（把阳离子/阴离子单独放 PySCF 算）
    # 这是快的（单离子 19-23 原子，比离子对 24-40 原子快）

    # 统计可提取的孤立离子构型数
    cat_n = {name: ILS[name]["cat"][1] for name in ILS}
    an_n = {name: ILS[name]["an"][1] for name in ILS}
    print("\n=== EDT 数据需求 ===")
    for name, recs in pairs.items():
        # 每个离子对提供 1 个阳离子 + 1 个阴离子孤立构型
        print(f"  {name}: {len(recs)} 阳离子构型 + {len(recs)} 阴离子构型（可算孤立能量）")

    total_pairs = sum(len(v) for v in pairs.values())
    print(f"\n总计 {total_pairs} 个离子对，可提取 {total_pairs} 组孤立离子能量")
    print("→ EDT: E_cat/E_an 用孤立能量训练，E_int 用残差，验证降低数据需求")

if __name__ == "__main__":
    main()
