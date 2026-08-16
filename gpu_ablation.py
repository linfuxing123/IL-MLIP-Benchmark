# -*- coding: utf-8 -*-
"""gpu_ablation.py — GPU 快速消融实验：隔离变量找 benchmark 数据质量根因。

实验矩阵（GPU 快速，每个 ~2 分钟）：
A. dft_il_rdkit 30 个（高质量基准）+ GPU → 确认 GPU 能否复现 37.6/59.8
B. benchmark 去掉坏构型 + GPU → 看是否改善
"""
import json
import pathlib
import subprocess
import numpy as np

MACE_TRAIN = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Lib\site-packages\mace\cli\run_train.py"
PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"

def to_xyz(recs, path):
    with open(path, "w", encoding="utf-8") as f:
        for r in recs:
            n = len(r["symbols"])
            e = r["energy"] * 27.2114
            f.write(f"{n}\nenergy={e:.8f} config_type=Default name={r.get('name','mol')}\n")
            for s, p in zip(r["symbols"], r["positions"]):
                f.write(f"{s} {p[0]:.8f} {p[1]:.8f} {p[2]:.8f}\n")

def run_mace(xyz_path, name, device="cuda", dtype="float32", epochs=100):
    cmd = [PY, MACE_TRAIN, "--name", name,
           "--train_file", str(xyz_path), "--valid_fraction", "0.15",
           "--energy_key", "energy",
           "--foundation_model", r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model",
           "--E0s", "average", "--max_num_epochs", str(epochs),
           "--batch_size", "4", "--device", device, "--default_dtype", dtype,
           "--seed", "42", "--model_dir", str(pathlib.Path(r"D:\Codex\MEC-Workspace\data") / f"ablation_{name}")]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    # 提取 RMSE
    import re
    out = r.stdout or ""
    rmse = None
    for line in out.splitlines():
        m = re.search(r"valid_Default\s*\|\s*([\d.]+)", line)
        if m:
            rmse = float(m.group(1))
    return rmse, out

# 实验 A：高质量基准 + GPU
old = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl", encoding="utf-8")]
es = np.array([r["energy"] for r in old])
print(f"实验 A: dft_il_rdkit {len(old)} 个, std {es.std()*1000:.0f} mHa")
xyz_a = r"D:\Codex\MEC-Workspace\data\ablation_a.xyz"
to_xyz(old, xyz_a)
rmse_a, _ = run_mace(xyz_a, "A_baseline_gpu", device="cuda", dtype="float32")
print(f"  结果: valid RMSE = {rmse_a} meV/atom", flush=True)

# 实验 B：benchmark 严格清理后的数据（用能量中位数±2.5 Ha 的宽松阈值重提取）
bench = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\il_benchmark\EMIM-BF4.jsonl", encoding="utf-8")]
es_b = np.array([r["energy"] for r in bench])
med = np.median(es_b)
# 只删能量偏离 >2.5 Ha 的（明显坏构型），保留正常范围
bench_clean = [r for r in bench if abs(r["energy"] - med) <= 2.5]
es_bc = np.array([r["energy"] for r in bench_clean])
print(f"\n实验 B: benchmark 去坏构型 {len(bench_clean)} 个, std {es_bc.std()*1000:.0f} mHa")
xyz_b = r"D:\Codex\MEC-Workspace\data\ablation_b.xyz"
to_xyz(bench_clean, xyz_b)
rmse_b, _ = run_mace(xyz_b, "B_bench_clean_gpu", device="cuda", dtype="float32")
print(f"  结果: valid RMSE = {rmse_b} meV/atom", flush=True)

print(f"\n=== 结论 ===")
print(f"基准(A): {rmse_a} meV/atom（之前 float64 CPU 是 59.8）")
print(f"benchmark去坏(B): {rmse_b} meV/atom")
if rmse_a is not None and rmse_a < 80:
    print("→ GPU 能复现基准精度，问题在 benchmark 数据质量")
elif rmse_b is not None and rmse_b < 80:
    print("→ 去坏构型后 benchmark 恢复精度，坏构型是根因")
else:
    print("→ 需进一步排查")
