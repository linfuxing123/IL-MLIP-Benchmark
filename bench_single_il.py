# -*- coding: utf-8 -*-
"""bench_single_il.py — 用 benchmark 的 EMIM-BF4 60 个数据跑单 IL MACE 微调。

验证：① benchmark 数据质量（统一 seed 协议）；② GPU 训练；③ 60 样本 vs 之前 30 样本。
"""
import json
import pathlib
import subprocess

BENCH = pathlib.Path(r"D:\Codex\MEC-Workspace\data\il_benchmark")
MACE_TRAIN = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Lib\site-packages\mace\cli\run_train.py"
PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"

# 加载 EMIM-BF4 60 个
recs = [json.loads(l) for l in open(BENCH / "EMIM-BF4.jsonl", encoding="utf-8")]
print(f"EMIM-BF4 benchmark 数据: {len(recs)} 个", flush=True)

# 转 XYZ（energy-only）
xyz = BENCH / "emim_bf4_bench.xyz"
with open(xyz, "w", encoding="utf-8") as f:
    for r in recs:
        n = len(r["symbols"])
        e = r["energy"] * 27.2114
        f.write(f"{n}\nenergy={e:.8f} config_type=Default name=EMIM-BF4\n")
        for s, p in zip(r["symbols"], r["positions"]):
            f.write(f"{s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}\n")
print(f"XYZ: {xyz}", flush=True)

# 跑 MACE 微调（GPU）
cmd = [PY, MACE_TRAIN, "--name", "bench_emim_bf4",
       "--train_file", str(xyz), "--valid_fraction", "0.15",
       "--energy_key", "energy",
       "--foundation_model", r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model",
       "--E0s", "average", "--max_num_epochs", "150",
       "--batch_size", "4", "--device", "cuda", "--default_dtype", "float32",
       "--seed", "42", "--model_dir", str(BENCH / "mace_bench_emim_bf4")]
print("跑 MACE 微调（GPU）...", flush=True)
r = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
tail = (r.stdout or "").splitlines()[-18:]
print("\n".join(tail), flush=True)
if r.returncode != 0:
    print("stderr:", (r.stderr or "")[-500:], flush=True)
