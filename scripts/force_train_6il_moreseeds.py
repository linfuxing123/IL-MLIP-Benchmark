# -*- coding: utf-8 -*-
"""force_train_6il_moreseeds.py — 补跑 6 IL 的 seed 7 和 123（seed42 已有）。

与 EMIM-BF4/Pyr14-FSI 同口径（3 seed），让 8-IL 力表有完整统计。
32ch float32 CPU OMP=4，l0 SWA / l2 EMA。
"""
import subprocess, os, sys, json
import numpy as np

PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"
CLI = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Lib\site-packages\mace\cli\run_train.py"
SRC_DIR = r"D:\Codex\MEC-Workspace\data\il_force"
BASE = r"D:\Codex\MEC-Workspace\data\il_force_models"

ILS = ["EMIM-PF6", "EMIM-NTf2", "BMIM-BF4", "BMIM-PF6", "BMIM-NTf2", "Pyr14-NTf2"]
SEEDS = ["7", "123"]  # seed42 already done


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
    n_test = min(15, nframes // 3)
    n_train = min(30, nframes - n_test)
    wxyz(os.path.join(out, "test_15.xyz"), [frames[i] for i in idx[:n_test]])
    wxyz(os.path.join(out, "train_30.xyz"), [frames[i] for i in idx[n_test:n_test+n_train]])
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
    env["OMP_NUM_THREADS"] = "4"
    env["MKL_NUM_THREADS"] = "4"
    print(f"\n=== 训练 {name} ===", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", env=env)
    if "Done" in r.stdout:
        print(f"OK {name}", flush=True)
        return True
    else:
        print(f"!! {name} 失败 rc={r.returncode}", flush=True)
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
            for seed in SEEDS:
                name = f"force_{il}_{lmax}_s{seed}_32ch"
                md = os.path.join(BASE, il, name)
                ok = train(name, irreps, md, train_file, test_file, seed, use_swa, use_ema)
                il_results.append({"il": il, "lmax": lmax, "seed": seed, "ok": ok})
        results[il] = il_results
        print(f"\n=== {il} 完成 ===", flush=True)
    out = os.path.join(BASE, "force_6il_moreseeds_summary.json")
    with open(out, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n=== 全部完成 ===\nsummary -> {out}", flush=True)


if __name__ == "__main__":
    main()
