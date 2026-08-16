# -*- coding: utf-8 -*-
"""run_mace_finetune.py — 调用 MACE run_train 微调。"""
import subprocess
import sys

PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"
MACE_TRAIN = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Lib\site-packages\mace\cli\run_train.py"

cmd = [
    PY, MACE_TRAIN,
    "--name", "il_finetune",
    "--train_file", r"D:\Codex\MEC-Workspace\data\il_train.xyz",
    "--valid_fraction", "0.2",
    "--energy_key", "energy",
    "--foundation_model", "small",   # 从 MACE-MP-0 small 初始化
    "--E0s", "average",              # 能量参考（自动）
    "--max_num_epochs", "500",
    "--batch_size", "8",
    "--device", "cpu",
    "--default_dtype", "float64",
    "--seed", "42",
    "--model_dir", r"D:\Codex\MEC-Workspace\data\mace_finetune_out",
]

r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
print("stdout tail:", (r.stdout or "")[-500:])
print("stderr tail:", (r.stderr or "")[-500:])
print("rc:", r.returncode)
