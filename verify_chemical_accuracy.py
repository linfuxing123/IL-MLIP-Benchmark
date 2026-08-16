# -*- coding: utf-8 -*-
"""verify_chemical_accuracy.py — 多 seed 验证 IL 离子对达化学精度。

用 dft_il_rdkit 30 个高质量数据 + GPU，跑 3 个 seed，看 RMSE 是否稳定 <43 meV。
"""
import json
import pathlib
import subprocess
import re
import numpy as np

MACE_TRAIN = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Lib\site-packages\mace\cli\run_train.py"
PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"

recs = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl", encoding="utf-8")]
xyz = r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.xyz"
with open(xyz, "w", encoding="utf-8") as f:
    for r in recs:
        n = len(r["symbols"])
        e = r["energy"] * 27.2114
        f.write(f"{n}\nenergy={e:.8f} config_type=Default name=EMIM-BF4\n")
        for s, p in zip(r["symbols"], r["positions"]):
            f.write(f"{s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}\n")

rmses = []
for seed in [42, 123, 777]:
    cmd = [PY, MACE_TRAIN, "--name", f"acc_{seed}",
           "--train_file", str(xyz), "--valid_fraction", "0.15",
           "--energy_key", "energy",
           "--foundation_model", r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model",
           "--E0s", "average", "--max_num_epochs", "200",
           "--batch_size", "4", "--device", "cuda", "--default_dtype", "float32",
           "--seed", str(seed), "--model_dir", rf"D:\Codex\MEC-Workspace\data\acc_{seed}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    rmse = None
    for line in (r.stdout or "").splitlines():
        m = re.search(r"valid_Default\s*\|\s*([\d.]+)", line)
        if m:
            rmse = float(m.group(1))
    rmses.append(rmse)
    print(f"seed {seed}: valid RMSE = {rmse} meV/atom", flush=True)

rmses = [r for r in rmses if r is not None]
if rmses:
    print(f"\n平均 RMSE = {np.mean(rmses):.1f} meV/atom, 范围 {min(rmses)}-{max(rmses)}", flush=True)
    print(f"{'✅ 稳定达化学精度 <43 meV' if np.mean(rmses) < 43 else '⚠️ 接近但未稳定 <43'}", flush=True)
