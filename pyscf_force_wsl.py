# -*- coding: utf-8 -*-
"""pyscf_force_wsl.py — WSL 里 PySCF 算 EMIM-BF4 力，存文件。"""
import json
import numpy as np

def pyscf_force(symbols, positions):
    from pyscf import gto, dft
    atom = [(s, (float(x), float(y), float(z))) for s, (x, y, z) in zip(symbols, positions)]
    mol = gto.M(atom=atom, basis="sto-3g", verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    mf.kernel()
    grad = mf.nuc_grad_method().kernel()
    return (-np.array(grad)).tolist()  # 力 = -梯度（Hartree/Bohr）

recs = [json.loads(l) for l in open(r"/mnt/d/Codex/MEC-Workspace/data/il_benchmark_clean/EMIM-BF4.jsonl", encoding="utf-8")]
n = min(10, len(recs))
print(f"算 {n} 个构型的 PySCF 力", flush=True)

out = []
for r in recs[:n]:
    f = pyscf_force(r["symbols"], r["positions"])
    out.append({"id": r["id"], "forces": f, "symbols": r["symbols"],
                "positions": r["positions"]})
    print(f"  {r['id']} 完成", flush=True)

with open(r"/mnt/d/Codex/MEC-Workspace/data/pyscf_forces.json", "w", encoding="utf-8") as f:
    json.dump(out, f)
print(f"完成 → /mnt/d/Codex/MEC-Workspace/data/pyscf_forces.json", flush=True)
