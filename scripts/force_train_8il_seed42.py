# -*- coding: utf-8 -*-
"""force_train_8il_seed42.py — 8 IL 力训练（单 seed 42，与 §2.3 能量表同口径）。

已完成的 EMIM-BF4 和 Pyr14-FSI（3 seed）跳过；
新增 6 IL 各 l0/l2 × seed42 = 12 模型。

32ch float32 CPU OMP=4（验证稳定）。
l0: SWA, l2: EMA。
"""
import subprocess, os, sys, json
import numpy as np

PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"
CLI = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Lib\site-packages\mace\cli\run_train.py"
SRC_DIR = r"D:\Codex\MEC-Workspace\data\il_force"
BASE = r"D:\Codex\MEC-Workspace\data\il_force_models"

# 6 ILs not yet trained (EMIM-BF4 + Pyr14-FSI already done with 3 seeds)
ILS = ["EMIM-PF6", "EMIM-NTf2", "BMIM-BF4", "BMIM-PF6", "BMIM-NTf2", "Pyr14-NTf2"]
SEED = "42"
N_TEST = 15
N_TRAIN = 30


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
    n_test = min(N_TEST, nframes // 3)
    n_train = min(N_TRAIN, nframes - n_test)
    wxyz(os.path.join(out, "test_15.xyz"), [frames[i] for i in idx[:n_test]])
    wxyz(os.path.join(out, "train_30.xyz"), [frames[i] for i in idx[n_test:n_test+n_train]])
    return os.path.join(out, "test_15.xyz"), os.path.join(out, "train_30.xyz")


def train(name, irreps, model_dir, train_file, valid_file, use_swa, use_ema):
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
        f"--seed={SEED}",
    ]
    if use_swa:
        cmd.append("--swa")
    if use_ema:
        cmd += ["--ema", "--ema_decay=0.99"]
    env = dict(os.environ)
    env["OMP_NUM_THREADS"] = "4"
    env["MKL_NUM_THREADS"] = "4"
    print(f"\n=== 训练 {name} ({'swa' if use_swa else 'ema'}) ===", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env)
    lines = r.stdout.splitlines()
    for i, ln in enumerate(lines):
        if "valid_Default" in ln:
            for j in range(max(0,i-4), min(len(lines),i+2)):
                print(lines[j], flush=True)
    if "Done" in r.stdout:
        print(f"OK {name}", flush=True)
        return True
    else:
        print(f"!! {name} 失败 rc={r.returncode}", flush=True)
        if r.stderr:
            print(f"   stderr: {r.stderr[-300:]}", flush=True)
        return False


def main():
    results = {}
    for il in ILS:
        test_file, train_file = split_data(il)
        il_results = []
        for lmax, irreps, use_swa, use_ema in [
            ("l0", "32x0e", True, False),
            ("l2", "32x0e+32x1o+32x2e", False, True),
        ]:
            name = f"force_{il}_{lmax}_s{SEED}_32ch"
            md = os.path.join(BASE, il, name)
            ok = train(name, irreps, md, train_file, test_file, use_swa, use_ema)
            il_results.append({"il": il, "lmax": lmax, "seed": SEED, "ok": ok})
        results[il] = il_results
        print(f"\n=== {il} 完成 ===", flush=True)

    out = os.path.join(BASE, "force_8il_seed42_summary.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n=== 全部完成 ===\nsummary -> {out}", flush=True)


if __name__ == "__main__":
    main()
