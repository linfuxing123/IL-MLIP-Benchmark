# -*- coding: utf-8 -*-
"""pyscf_force_all.py — WSL 补算 EMIM-BF4 60 个构型的力（含能量），转 XYZ。"""
import json
import numpy as np

def energy_force(symbols, positions):
    from pyscf import gto, dft
    atom = [(s, (float(x), float(y), float(z))) for s, (x, y, z) in zip(symbols, positions)]
    mol = gto.M(atom=atom, basis="sto-3g", verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    e = mf.kernel()
    grad = mf.nuc_grad_method().kernel()
    return e, (-np.array(grad))  # 力 = -梯度（Hartree/Bohr）

recs = [json.loads(l) for l in open(r"/mnt/d/Codex/MEC-Workspace/data/il_benchmark_clean/EMIM-BF4.jsonl", encoding="utf-8")]
print(f"算 {len(recs)} 个构型的能量+力（PySCF B3LYP/STO-3G）", flush=True)

# 转 extended XYZ（含能量 + 力）
out_lines = []
for r in recs:
    e, f = energy_force(r["symbols"], r["positions"])
    n = len(r["symbols"])
    e_ev = e * 27.2114
    f_evA = f * 27.2114 / 0.529177
    out_lines.append(f"{n}\nenergy={e_ev:.8f} config_type=Default name=EMIM-BF4 REF_forces=" + 
                     " ".join(f"{v:.8f}" for v in f_evA.flatten()))
    for s, p in zip(r["symbols"], r["positions"]):
        out_lines.append(f"{s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}")
    if len(out_lines) % 200 == 0:
        print(f"  {len(out_lines)//(n+2)}/{len(recs)} 完成", flush=True)

with open(r"/mnt/d/Codex/MEC-Workspace/data/emim_bf4_force.xyz", "w", encoding="utf-8") as f:
    f.write("\n".join(out_lines) + "\n")
print(f"完成 → /mnt/d/Codex/MEC-Workspace/data/emim_bf4_force.xyz（{len(recs)} 帧，含力）", flush=True)
