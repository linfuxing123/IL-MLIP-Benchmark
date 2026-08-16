# -*- coding: utf-8 -*-
"""test_ase_read.py — 用 ASE 读 XYZ，看力在哪（info vs arrays）。"""
import ase.io

atoms_list = ase.io.read(r"D:\Codex\MEC-Workspace\data\emim_bf4_force.xyz", index=":")
a = atoms_list[0]
print("atoms.info keys:", list(a.info.keys()))
print("atoms.arrays keys:", list(a.arrays.keys()))
print("\ninfo['REF_forces'] 类型:", type(a.info.get("REF_forces", None)))
print("arrays['REF_forces'] 存在:", "REF_forces" in a.arrays)
if "REF_forces" in a.arrays:
    print("arrays['REF_forces'] 形状:", a.arrays["REF_forces"].shape)
