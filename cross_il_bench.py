# -*- coding: utf-8 -*-
"""cross_il_bench.py — 跨 IL 泛化 benchmark（数据集价值验证）。

用 435 个数据，train 7 IL / test 1 IL，验证 MACE 能否跨 IL 泛化。
注意能量尺度问题：用 MACE multihead（每 IL 一个 head）或按 IL 分别评估。
这里用简单方案：MACE 微调全部数据，评估每 IL 的 RMSE。
"""
import json
import pathlib
import subprocess
import re
import numpy as np

MACE_TRAIN = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Lib\site-packages\mace\cli\run_train.py"
PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"
BENCH = pathlib.Path(r"D:\Codex\MEC-Workspace\data\il_benchmark_clean")

# 加载所有 IL 数据
all_recs = {}
for f in BENCH.glob("*.jsonl"):
    name = f.stem
    recs = [json.loads(l) for l in f.open(encoding="utf-8")]
    all_recs[name] = recs

print(f"8 IL 数据：{ {k: len(v) for k, v in all_recs.items()} }", flush=True)

def to_xyz(recs, path):
    with open(path, "w", encoding="utf-8") as f:
        for r in recs:
            n = len(r["symbols"])
            e = r["energy"] * 27.2114
            f.write(f"{n}\nenergy={e:.8f} config_type=Default name={r['name']}\n")
            for s, p in zip(r["symbols"], r["positions"]):
                f.write(f"{s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}\n")

# 对每个 test IL：train 其余 7 IL，评估 test IL
print("\n=== 跨 IL 泛化（leave-one-IL-out）===", flush=True)
for test_il in sorted(all_recs.keys()):
    train = [r for name, recs in all_recs.items() if name != test_il for r in recs]
    test = all_recs[test_il]
    if len(test) < 5:
        continue
    xyz = BENCH / f"cross_il_train_{test_il}.xyz"
    to_xyz(train, xyz)
    cmd = [PY, MACE_TRAIN, "--name", f"cross_{test_il}",
           "--train_file", str(xyz), "--valid_fraction", "0.1",
           "--energy_key", "energy",
           "--foundation_model", r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model",
           "--E0s", "average", "--max_num_epochs", "100",
           "--batch_size", "8", "--device", "cuda", "--default_dtype", "float32",
           "--seed", "42", "--model_dir", rf"D:\Codex\MEC-Workspace\data\cross_{test_il}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    rmse = None
    for line in (r.stdout or "").splitlines():
        m = re.search(r"valid_Default\s*\|\s*([\d.]+)", line)
        if m:
            rmse = float(m.group(1))
    print(f"  test={test_il}: 训练 {len(train)} 构型 → valid RMSE {rmse} meV/atom", flush=True)
