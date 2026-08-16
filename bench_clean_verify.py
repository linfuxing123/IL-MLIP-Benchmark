# -*- coding: utf-8 -*-
"""bench_clean_verify.py — 用清理后的干净 EMIM-BF4 数据重跑单 IL MACE 微调。

验证：清理异常数据后，benchmark 数据质量是否恢复（对比之前 9411 meV）。
"""
import json
import pathlib
import subprocess

BENCH = pathlib.Path(r"D:\Codex\MEC-Workspace\data\il_benchmark")
MACE_TRAIN = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Lib\site-packages\mace\cli\run_train.py"
PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"

recs = [json.loads(l) for l in open(BENCH / "EMIM-BF4.jsonl", encoding="utf-8")]
import numpy as np
es = np.array([r["energy"] for r in recs])
print(f"EMIM-BF4 干净数据: {len(recs)} 个, 能量 {es.min():.4f}~{es.max():.4f} Ha, std {es.std()*1000:.0f} mHa", flush=True)

xyz = BENCH / "emim_bf4_clean.xyz"
with open(xyz, "w", encoding="utf-8") as f:
    for r in recs:
        n = len(r["symbols"])
        e = r["energy"] * 27.2114
        f.write(f"{n}\nenergy={e:.8f} config_type=Default name=EMIM-BF4\n")
        for s, p in zip(r["symbols"], r["positions"]):
            f.write(f"{s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}\n")

cmd = [PY, MACE_TRAIN, "--name", "bench_clean_f64",
       "--train_file", str(xyz), "--valid_fraction", "0.15",
       "--energy_key", "energy",
       "--foundation_model", r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model",
       "--E0s", "average", "--max_num_epochs", "150",
       "--batch_size", "4", "--device", "cpu", "--default_dtype", "float64",
       "--seed", "42", "--model_dir", str(BENCH / "mace_bench_clean_f64")]
print("跑 MACE 微调（float64 CPU，对比 float32 GPU）...", flush=True)
r = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
tail = (r.stdout or "").splitlines()[-14:]
print("\n".join(tail), flush=True)
