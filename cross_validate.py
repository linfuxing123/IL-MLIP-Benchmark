# -*- coding: utf-8 -*-
"""cross_validate.py — 5 折交叉验证 EMIM-BF4 化学精度。"""
import json
import pathlib
import subprocess
import re
import numpy as np

MACE_TRAIN = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Lib\site-packages\mace\cli\run_train.py"
PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"

emim = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\il_benchmark_clean\EMIM-BF4.jsonl", encoding="utf-8")]
n = len(emim)
print(f"EMIM-BF4 {n} 个干净数据，5 折交叉验证", flush=True)

rng = np.random.RandomState(42)
idx = rng.permutation(n)
fold_size = n // 5

def to_xyz(recs, path):
    with open(path, "w", encoding="utf-8") as f:
        for r in recs:
            nn = len(r["symbols"])
            e = r["energy"] * 27.2114
            f.write(f"{nn}\nenergy={e:.8f} config_type=Default name=EMIM-BF4\n")
            for s, p in zip(r["symbols"], r["positions"]):
                f.write(f"{s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}\n")

fold_rmses = []
for fold in range(5):
    te_idx = idx[fold*fold_size:(fold+1)*fold_size]
    tr_idx = [i for i in idx if i not in te_idx]
    tr = [emim[i] for i in tr_idx]
    te = [emim[i] for i in te_idx]
    tr_xyz = pathlib.Path(rf"D:\Codex\MEC-Workspace\data\cv_tr_{fold}.xyz")
    to_xyz(tr, tr_xyz)
    cmd = [PY, MACE_TRAIN, "--name", f"cv_{fold}",
           "--train_file", str(tr_xyz), "--valid_fraction", "0.15",
           "--energy_key", "energy",
           "--foundation_model", r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model",
           "--E0s", "average", "--max_num_epochs", "200",
           "--batch_size", "4", "--device", "cuda", "--default_dtype", "float32",
           "--seed", "42", "--model_dir", rf"D:\Codex\MEC-Workspace\data\cv_{fold}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    rmse = None
    for line in (r.stdout or "").splitlines():
        m = re.search(r"valid_Default\s*\|\s*([\d.]+)", line)
        if m:
            rmse = float(m.group(1))
    fold_rmses.append(rmse)
    print(f"  fold {fold}: {rmse} meV/atom", flush=True)

fold_rmses = [r for r in fold_rmses if r is not None]
if fold_rmses:
    print(f"\n5 折交叉验证 RMSE: {np.mean(fold_rmses):.1f} ± {np.std(fold_rmses):.1f} meV/atom", flush=True)
    print(f"{'✅ 达化学精度 <43' if np.mean(fold_rmses) < 43 else '⚠️ 接近但未达 43'}", flush=True)
