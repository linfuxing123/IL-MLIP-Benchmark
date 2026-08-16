# -*- coding: utf-8 -*-
"""bench_quality_check.py — 用 42 个高质量 EMIM-BF4 跑 MACE 微调，验证质量修复。"""
import json
import pathlib
import subprocess
import numpy as np

MACE_TRAIN = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Lib\site-packages\mace\cli\run_train.py"
PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"

recs = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\il_benchmark\EMIM-BF4.jsonl", encoding="utf-8")]
es = np.array([r["energy"] for r in recs])
print(f"EMIM-BF4 高质量数据: {len(recs)} 个, std {es.std()*1000:.0f} mHa", flush=True)

xyz = r"D:\Codex\MEC-Workspace\data\il_benchmark\emim_bf4_q.xyz"
with open(xyz, "w", encoding="utf-8") as f:
    for r in recs:
        n = len(r["symbols"])
        e = r["energy"] * 27.2114
        f.write(f"{n}\nenergy={e:.8f} config_type=Default name=EMIM-BF4\n")
        for s, p in zip(r["symbols"], r["positions"]):
            f.write(f"{s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}\n")

cmd = [PY, MACE_TRAIN, "--name", "bench_q",
       "--train_file", str(xyz), "--valid_fraction", "0.15",
       "--energy_key", "energy",
       "--foundation_model", r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model",
       "--E0s", "average", "--max_num_epochs", "150",
       "--batch_size", "4", "--device", "cuda", "--default_dtype", "float32",
       "--seed", "42", "--model_dir", r"D:\Codex\MEC-Workspace\data\mace_bench_q"]
print("跑 MACE 微调（GPU）...", flush=True)
r = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
tail = (r.stdout or "").splitlines()[-12:]
print("\n".join(tail), flush=True)
