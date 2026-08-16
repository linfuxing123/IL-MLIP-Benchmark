# -*- coding: utf-8 -*-
"""mace_force_win.py — Windows 里 MACE 力预测，对比 PySCF 力，算 RMSE。"""
import json
import numpy as np

from mace.calculators import MACECalculator
from ase import Atoms

# 读 PySCF 参考力
ref = json.loads(open(r"D:\Codex\MEC-Workspace\data\pyscf_forces.json", encoding="utf-8").read())
print(f"PySCF 参考力: {len(ref)} 个构型", flush=True)

# MACE-MP-0 力预测
calc = MACECalculator(model_paths=r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model",
                      default_dtype="float64", device="cuda")

force_refs, force_preds = [], []
for r in ref:
    # PySCF 力：Hartree/Bohr → eV/Å
    f_ref = np.array(r["forces"]) * 27.2114 / 0.529177
    force_refs.append(f_ref)
    # MACE 力
    atoms = Atoms(symbols=r["symbols"], positions=r["positions"], calculator=calc)
    f_pred = atoms.get_forces()  # eV/Å
    force_preds.append(f_pred)

force_refs = np.array(force_refs)
force_preds = np.array(force_preds)
diff = force_preds - force_refs
rmse = np.sqrt((diff**2).mean()) * 1000  # meV/Å
mae = np.abs(diff).mean() * 1000

print(f"\n力 RMSE = {rmse:.0f} meV/Å", flush=True)
print(f"力 MAE = {mae:.0f} meV/Å", flush=True)
print(f"力分量 RMSE: x={np.sqrt((diff[:,:,0]**2).mean())*1000:.0f}, "
      f"y={np.sqrt((diff[:,:,1]**2).mean())*1000:.0f}, "
      f"z={np.sqrt((diff[:,:,2]**2).mean())*1000:.0f} meV/Å", flush=True)
print(f"\n（参考：力 RMSE < 50 meV/Å 通常视为合格）", flush=True)
