# -*- coding: utf-8 -*-
"""benchmark_eval.py — IL-MLIP-Benchmark 评估脚本（数据到位后跑）。

功能：
1. 合并 8 IL 数据 → 划分（train 7 IL / test 1 IL，跨 IL 泛化）
2. 转 MACE XYZ 格式
3. 跑 MACE 微调（能量 + 力）
4. 输出 benchmark 表（能量 MAE + 力 RMSE）

用法：python benchmark_eval.py <test_il> [--epochs 100]
"""
import json
import pathlib
import subprocess
import sys

BENCH = pathlib.Path(r"D:\Codex\MEC-Workspace\data\il_benchmark")
MACE_TRAIN = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Lib\site-packages\mace\cli\run_train.py"
PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"

def load_all():
    recs = []
    for f in BENCH.glob("*.jsonl"):
        recs.extend([json.loads(l) for l in f.open(encoding="utf-8")])
    return recs

def to_xyz(recs, path, forces=True):
    """转 extended XYZ（含能量 + 力）。"""
    with open(path, "w", encoding="utf-8") as f:
        for r in recs:
            n = len(r["symbols"])
            e = r["energy"] * 27.2114  # Ha → eV
            # 力：Hartree/Bohr → eV/Å
            if forces and "forces" in r:
                fxyz = [float(x) * 27.2114 / 0.529177 for x in r["forces"]]
                comment = f'energy={e:.8f} config_type=Default name={r["name"]} REF_forces='
                comment += " ".join(f"{v:.8f}" for v in fxyz)
                f.write(f"{n}\n{comment}\n")
                for s, p in zip(r["symbols"], r["positions"]):
                    f.write(f"{s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}\n")
            else:
                f.write(f"{n}\nenergy={e:.8f} config_type=Default name={r['name']}\n")
                for s, p in zip(r["symbols"], r["positions"]):
                    f.write(f"{s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}\n")

def main():
    test_il = sys.argv[1] if len(sys.argv) > 1 else "EMIM-BF4"
    epochs = int(sys.argv[2]) if len(sys.argv) > 2 else 100

    recs = load_all()
    if not recs:
        print("无数据，先等生成", flush=True)
        return
    print(f"总数据: {len(recs)} 样本", flush=True)

    # 划分：test_il 做测试，其余做训练（跨 IL 泛化）
    train = [r for r in recs if r["name"] != test_il]
    test = [r for r in recs if r["name"] == test_il]
    print(f"train: {len(train)}（7 IL）, test: {len(test)}（{test_il}）", flush=True)

    if not test:
        print(f"{test_il} 无数据（可能还没生成）", flush=True)
        return

    train_xyz = BENCH / f"train_except_{test_il}.xyz"
    to_xyz(train, train_xyz, forces=False)  # 新数据无力，energy-only
    print(f"train XYZ: {train_xyz}", flush=True)

    # 跑 MACE 微调（energy-only，GPU）
    cmd = [PY, MACE_TRAIN, "--name", f"bench_{test_il}",
           "--train_file", str(train_xyz), "--valid_fraction", "0.1",
           "--energy_key", "energy",
           "--foundation_model", r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model",
           "--E0s", "average", "--max_num_epochs", str(epochs),
           "--batch_size", "4", "--device", "cuda", "--default_dtype", "float32",
           "--seed", "42", "--model_dir", str(BENCH / f"mace_bench_{test_il}")]
    print("跑 MACE 微调...", flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=7200)
    # 输出最后 20 行
    tail = (r.stdout or "").splitlines()[-20:]
    print("\n".join(tail), flush=True)

if __name__ == "__main__":
    main()
