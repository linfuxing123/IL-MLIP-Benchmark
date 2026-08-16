# -*- coding: utf-8 -*-
"""bench_clean_final.py — 用过滤后的干净数据跑最终 benchmark。"""
import json
import pathlib
import subprocess
import re
import numpy as np

MACE_TRAIN = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Lib\site-packages\mace\cli\run_train.py"
PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"
BENCH = pathlib.Path(r"D:\Codex\MEC-Workspace\data\il_benchmark_clean")

def to_xyz(recs, path):
    with open(path, "w", encoding="utf-8") as f:
        for r in recs:
            n = len(r["symbols"])
            e = r["energy"] * 27.2114
            f.write(f"{n}\nenergy={e:.8f} config_type=Default name={r.get('name','mol')}\n")
            for s, p in zip(r["symbols"], r["positions"]):
                f.write(f"{s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}\n")

def run_mace(xyz, name, seed, epochs=200):
    cmd = [PY, MACE_TRAIN, "--name", name,
           "--train_file", str(xyz), "--valid_fraction", "0.15",
           "--energy_key", "energy",
           "--foundation_model", r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model",
           "--E0s", "average", "--max_num_epochs", str(epochs),
           "--batch_size", "4", "--device", "cuda", "--default_dtype", "float32",
           "--seed", str(seed), "--model_dir", str(pathlib.Path(r"D:\Codex\MEC-Workspace\data") / f"cf_{name}")]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    rmse = None
    for line in (r.stdout or "").splitlines():
        m = re.search(r"valid_Default\s*\|\s*([\d.]+)", line)
        if m:
            rmse = float(m.group(1))
    return rmse

# EMIM-BF4 单 IL 化学精度（多 seed）
emim = [json.loads(l) for l in open(BENCH / "EMIM-BF4.jsonl", encoding="utf-8")]
es = np.array([r["energy"] for r in emim])
print(f"EMIM-BF4 干净数据: {len(emim)} 个, std {es.std()*1000:.0f} mHa", flush=True)
xyz = BENCH / "emim_clean.xyz"
to_xyz(emim, xyz)

print("\n=== EMIM-BF4 化学精度（多 seed，200 epoch）===", flush=True)
rmses = []
for seed in [42, 123, 777, 2024]:
    rmse = run_mace(xyz, f"emim_c{seed}", seed)
    rmses.append(rmse)
    print(f"  seed {seed}: {rmse} meV/atom", flush=True)
rmses = [r for r in rmses if r is not None]
if rmses:
    print(f"  平均 {np.mean(rmses):.1f} meV/atom, 范围 {min(rmses)}-{max(rmses)}", flush=True)
    print(f"  {'✅ 稳定达化学精度 <43' if np.mean(rmses) < 43 else '⚠️ 平均未达 43'}", flush=True)
