# -*- coding: utf-8 -*-
"""test_quote_format.py — 测引号包裹的力格式能否被 ASE 正确解析。"""
import ase.io
import numpy as np

# 手动写一个带引号力的小 XYZ
lines = [
    "2",
    'energy=-100.0 config_type=Default name=test REF_forces="1.0 2.0 3.0 4.0 5.0 6.0" pbc="F F F"',
    "C 0 0 0",
    "H 0 0 1",
]
with open(r"D:\Codex\MEC-Workspace\data\test_quote.xyz", "w") as f:
    f.write("\n".join(lines) + "\n")

a = ase.io.read(r"D:\Codex\MEC-Workspace\data\test_quote.xyz")
print("arrays keys:", list(a.arrays.keys()))
print("REF_forces 在 arrays:", "REF_forces" in a.arrays)
if "REF_forces" in a.arrays:
    print("形状:", a.arrays["REF_forces"].shape, "值:", a.arrays["REF_forces"].flatten())
