# -*- coding: utf-8 -*-
"""pyscf_force_json.py — WSL 算 EMIM-BF4 60 个的力+能量，输出 JSON。"""
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
    return float(e), (-np.array(grad)).tolist()  # 力 = -梯度（Hartree/Bohr）

recs = [json.loads(l) for l in open(r"/mnt/d/Codex/MEC-Workspace/data/il_benchmark_clean/EMIM-BF4.jsonl", encoding="utf-8")]
print(f"算 {len(recs)} 个构型的能量+力", flush=True)

out = []
for r in recs:
    e, f = energy_force(r["symbols"], r["positions"])
    out.append({"id": r["id"], "symbols": r["symbols"], "positions": r["positions"],
                "energy": e, "forces": f})
    if len(out) % 15 == 0:
        print(f"  {len(out)}/{len(recs)}", flush=True)

with open(r"/mnt/d/Codex/MEC-Workspace/data/emim_bf4_force.json", "w", encoding="utf-8") as fp:
    json.dump(out, fp)
print(f"完成 → /mnt/d/Codex/MEC-Workspace/data/emim_bf4_force.json（{len(out)} 帧）", flush=True)
