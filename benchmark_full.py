# -*- coding: utf-8 -*-
"""benchmark_full.py — IL-MLIP-Benchmark 完整评估（数据到位后跑）。

内容：
1. 数据质量汇总（各 IL 样本数 + 能量 std）
2. 单 IL MACE 微调（EMIM-BF4，多 seed 验证化学精度稳定性）
3. 数据量学习曲线（30 vs 60 个，看是否稳定 <43 meV）
"""
import json
import pathlib
import subprocess
import re
import numpy as np

MACE_TRAIN = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Lib\site-packages\mace\cli\run_train.py"
PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"
BENCH = pathlib.Path(r"D:\Codex\MEC-Workspace\data\il_benchmark")

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
           "--seed", str(seed), "--model_dir", str(pathlib.Path(r"D:\Codex\MEC-Workspace\data") / f"bf_{name}")]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    rmse = None
    for line in (r.stdout or "").splitlines():
        m = re.search(r"valid_Default\s*\|\s*([\d.]+)", line)
        if m:
            rmse = float(m.group(1))
    return rmse

# 1. 数据质量汇总
print("=== IL-MLIP-Benchmark 数据质量汇总 ===", flush=True)
all_recs = {}
for f in BENCH.glob("*.jsonl"):
    if f.name.startswith("train") or f.name.startswith("emim") or f.name.startswith("mace"):
        continue
    recs = [json.loads(l) for l in f.open(encoding="utf-8")]
    if recs:
        es = np.array([r["energy"] for r in recs])
        name = f.stem
        all_recs[name] = recs
        print(f"  {name}: {len(recs)} 个, 能量 std {es.std()*1000:.0f} mHa", flush=True)

# 2. EMIM-BF4 单 IL 化学精度（多 seed）
print("\n=== EMIM-BF4 单 IL 化学精度（多 seed）===", flush=True)
if "EMIM-BF4" in all_recs and len(all_recs["EMIM-BF4"]) >= 40:
    emim = all_recs["EMIM-BF4"]
    xyz = BENCH / "emim_full.xyz"
    to_xyz(emim, xyz)
    rmses = []
    for seed in [42, 123, 777, 2024]:
        rmse = run_mace(xyz, f"emim_s{seed}", seed)
        rmses.append(rmse)
        print(f"  seed {seed}: {rmse} meV/atom", flush=True)
    rmses = [r for r in rmses if r is not None]
    if rmses:
        print(f"  平均 {np.mean(rmses):.1f}, 范围 {min(rmses)}-{max(rmses)} meV/atom", flush=True)
        print(f"  {'✅ 稳定 <43' if np.mean(rmses) < 43 else '⚠️ 平均未达 43（数据量限制）'}", flush=True)

# 3. 数据量学习曲线
print("\n=== 数据量学习曲线（30 vs 全量）===", flush=True)
if "EMIM-BF4" in all_recs:
    emim = all_recs["EMIM-BF4"]
    for n_sub in [30, len(emim)]:
        sub = emim[:n_sub]
        xyz_sub = BENCH / f"emim_{n_sub}.xyz"
        to_xyz(sub, xyz_sub)
        rmse = run_mace(xyz_sub, f"emim_n{n_sub}", 42)
        print(f"  {n_sub} 个: {rmse} meV/atom", flush=True)
