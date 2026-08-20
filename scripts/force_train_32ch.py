# -*- coding: utf-8 -*-
"""force_train_32ch.py — 32ch l0 vs l2 力训练（CPU, float32, 1 thread）。

128ch l2 在 CPU 上 e3nn 崩溃（access violation），128ch l0 正常。
32ch float32 单线程 l2 稳定通过 20 epoch 测试。
用 32ch 对比 l0 vs l2（与论文 8-IL 对比同容量）。

用法: python force_train_32ch.py
"""
import subprocess, os, sys, json
import numpy as np

PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"
CLI = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Lib\site-packages\mace\cli\run_train.py"
SRC_DIR = r"D:\Codex\MEC-Workspace\data\il_force"
BASE = r"D:\Codex\MEC-Workspace\data\il_force_models"

ILS = ["EMIM-BF4", "Pyr14-FSI"]
SEEDS = ["7", "42", "123"]


def split_data(il):
    xyz = os.path.join(SRC_DIR, f"{il}_force.xyz")
    with open(xyz) as f:
        lines = f.readlines()
    natoms = int(lines[0].strip())
    nframes = len(lines) // (natoms + 2)
    frames = [lines[i*(natoms+2):(i+1)*(natoms+2)] for i in range(nframes)]
    rng = np.random.RandomState(42)
    idx = rng.permutation(nframes)
    out = os.path.join(SRC_DIR, f"split_{il}")
    os.makedirs(out, exist_ok=True)
    def wxyz(path, fl):
        with open(path, "w") as f:
            for frame in fl:
                f.writelines(frame)
    wxyz(os.path.join(out, "test_15.xyz"), [frames[i] for i in idx[:15]])
    wxyz(os.path.join(out, "train_30.xyz"), [frames[i] for i in idx[15:45]])
    return os.path.join(out, "test_15.xyz"), os.path.join(out, "train_30.xyz")


def train(name, irreps, model_dir, train_file, valid_file, seed, use_swa, use_ema):
    os.makedirs(model_dir, exist_ok=True)
    cmd = [
        PY, "-u", "-X", "utf8", CLI,
        f"--name={name}",
        f"--train_file={train_file}",
        f"--valid_file={valid_file}",
        f"--model_dir={model_dir}",
        f"--hidden_irreps={irreps}",
        "--r_max=5.0",
        "--batch_size=4",
        "--max_num_epochs=150",
        "--loss=ef",
        "--energy_weight=1.0",
        "--forces_weight=10.0",
        "--energy_key=energy",
        "--forces_key=forces",
        "--E0s=average",
        "--default_dtype=float32",
        "--device=cpu",
        "--num_workers=0",
        f"--seed={seed}",
    ]
    if use_swa:
        cmd.append("--swa")
    if use_ema:
        cmd += ["--ema", "--ema_decay=0.99"]
    env = dict(os.environ)
    env["OMP_NUM_THREADS"] = "1"
    env["MKL_NUM_THREADS"] = "1"
    print(f"\n=== 训练 {name} (32ch, f32, {'swa' if use_swa else 'ema'}) ===", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env)
    lines = r.stdout.splitlines()
    for i, ln in enumerate(lines):
        if "valid_Default" in ln and "RMSE" in ln:
            for j in range(max(0,i-4), min(len(lines),i+2)):
                print(lines[j], flush=True)
    if r.returncode != 0:
        print(f"!! {name} 失败 rc={r.returncode}: {r.stderr[-400:]}", flush=True)
        return False
    return True


def main():
    all_results = {}
    for il in ILS:
        test_file, train_file = split_data(il)
        il_results = []
        for lmax, irreps, use_swa, use_ema in [
            ("l0", "32x0e", True, False),
            ("l2", "32x0e+32x1o+32x2e", False, True),
        ]:
            for seed in SEEDS:
                name = f"force_{il}_{lmax}_s{seed}_32ch"
                md = os.path.join(BASE, il, name)
                ok = train(name, irreps, md, train_file, test_file, seed,
                           use_swa, use_ema)
                il_results.append({"il": il, "lmax": lmax, "seed": seed,
                                   "channels": 32, "ok": ok})
        all_results[il] = il_results
        print(f"\n=== {il} 32ch 训练完成 ===", flush=True)

    out = os.path.join(BASE, "force_32ch_summary.json")
    with open(out, "w") as f:
        json.dump(all_results, f, indent=2)
    print(f"\n=== 全部完成 ===\nsummary -> {out}", flush=True)


if __name__ == "__main__":
    main()
