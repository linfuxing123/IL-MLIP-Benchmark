# -*- coding: utf-8 -*-
"""test_ase_write.py — 测 ASE write 自动生成正确 extxyz 力格式。"""
import ase.io
import numpy as np
from ase import Atoms

a = Atoms(symbols=["C", "H"], positions=[[0,0,0],[0,0,1]])
a.arrays["REF_forces"] = np.array([[1,2,3],[4,5,6]], dtype=float)
a.info["REF_energy"] = -100.0
ase.io.write(r"D:\Codex\MEC-Workspace\data\test_ase_w.xyz", a, format="extxyz")

# 读回验证
b = ase.io.read(r"D:\Codex\MEC-Workspace\data\test_ase_w.xyz")
print("写出的内容:")
print(open(r"D:\Codex\MEC-Workspace\data\test_ase_w.xyz").read())
print("读回 arrays keys:", list(b.arrays.keys()))
print("REF_forces 在 arrays:", "REF_forces" in b.arrays)
if "REF_forces" in b.arrays:
    print("形状:", b.arrays["REF_forces"].shape)
