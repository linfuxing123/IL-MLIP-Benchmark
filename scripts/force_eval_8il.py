# -*- coding: utf-8 -*-
"""force_eval_8il.py — 评估全部 8 IL 力模型，生成 8-IL 力差距排序表。

EMIM-BF4 + Pyr14-FSI: 3 seed（已有）
其余 6 IL: seed 42（新增）
输出：8-IL force gap ranking + 与 energy gap ranking 对比。
"""
import os, sys, glob, json
import numpy as np
from ase.io import read
from mace.calculators import MACECalculator

BASE = r"D:\Codex\MEC-Workspace\data\il_force_models"
SPLIT_DIR = r"D:\Codex\MEC-Workspace\data\il_force"

ALL_ILS = [
    "EMIM-BF4", "EMIM-PF6", "EMIM-NTf2",
    "BMIM-BF4", "BMIM-PF6", "BMIM-NTf2",
    "Pyr14-FSI", "Pyr14-NTf2",
]

# Energy gap ranking from §2.3 (for comparison)
ENERGY_GAPS = {
    "BMIM-PF6":  +107.9, "EMIM-PF6":  +45.4,
    "Pyr14-FSI": +43.1,  "Pyr14-NTf2": +23.3,
    "BMIM-NTf2": +11.4,  "BMIM-BF4":   +3.5,
    "EMIM-BF4":  -8.1,   "EMIM-NTf2":  -11.5,
}

ANION_MAP = {
    "EMIM-BF4": "BF4", "EMIM-PF6": "PF6", "EMIM-NTf2": "NTf2",
    "BMIM-BF4": "BF4", "BMIM-PF6": "PF6", "BMIM-NTf2": "NTf2",
    "Pyr14-FSI": "FSI", "Pyr14-NTf2": "NTf2",
}

# Which seeds are available per IL (all 3 seeds after moreseeds training)
SEEDS_PER_IL = {
    "EMIM-BF4": ["7", "42", "123"],
    "Pyr14-FSI": ["7", "42", "123"],
    "EMIM-PF6": ["7", "42", "123"],
    "EMIM-NTf2": ["7", "42", "123"],
    "BMIM-BF4": ["7", "42", "123"],
    "BMIM-PF6": ["7", "42", "123"],
    "BMIM-NTf2": ["7", "42", "123"],
    "Pyr14-NTf2": ["7", "42", "123"],
}


def eval_model(model_dir, test_file, device="cpu"):
    cand = glob.glob(os.path.join(model_dir, "*_compiled.model"))
    if not cand:
        cand = glob.glob(os.path.join(model_dir, "*.model"))
    if not cand:
        return None, None, 0
    stagetwo = [c for c in cand if "stagetwo_compiled" in c]
    if stagetwo:
        cand = stagetwo
    try:
        calc = MACECalculator(model_paths=cand[0], default_dtype="float32",
                              device=device)
    except Exception as e:
        print(f"    load error: {e}", flush=True)
        return None, None, 0
    atoms = read(test_file, index=":")
    e_pred, e_ref, f_pred, f_ref = [], [], [], []
    for a in atoms:
        try:
            er = a.get_potential_energy()
            fr = a.get_forces()
        except Exception:
            continue
        a.calc = calc
        try:
            ep = a.get_potential_energy()
            fp = a.get_forces()
        except Exception as e:
            print(f"    predict error: {e}", flush=True)
            continue
        e_pred.append(ep); e_ref.append(er)
        f_pred.append(fp); f_ref.append(fr)
    if not e_pred:
        return None, None, 0
    e_pred = np.array(e_pred); e_ref = np.array(e_ref)
    f_pred = np.concatenate([f.reshape(-1) for f in f_pred])
    f_ref = np.concatenate([f.reshape(-1) for f in f_ref])
    natoms = len(atoms[0])
    e_rmse = np.sqrt(np.mean((e_pred - e_ref)**2)) / natoms * 1000
    f_rmse = np.sqrt(np.mean((f_pred - f_ref)**2)) * 1000
    return e_rmse, f_rmse, len(e_pred)


def main():
    all_rows = []
    summary = {}

    for il in ALL_ILS:
        test_file = os.path.join(SPLIT_DIR, f"split_{il}", "test_15.xyz")
        if not os.path.exists(test_file):
            print(f"!! {il}: 缺 test 文件", flush=True)
            continue

        seeds = SEEDS_PER_IL.get(il, ["42"])
        print(f"\n=== 评估 {il} (seeds: {seeds}) ===", flush=True)
        il_rows = []
        for lmax in ["l0", "l2"]:
            for seed in seeds:
                name = f"force_{il}_{lmax}_s{seed}_32ch"
                md = os.path.join(BASE, il, name)
                e, f, n = eval_model(md, test_file)
                if e is None:
                    print(f"  {name}: 缺失", flush=True)
                    continue
                print(f"  {name}: E={e:.1f} meV, F={f:.1f} meV/A (n={n})", flush=True)
                row = {"il": il, "lmax": lmax, "seed": seed,
                       "e_rmse_mev": round(e, 1),
                       "f_rmse_mevA": round(f, 1), "n_test": n}
                il_rows.append(row)
                all_rows.append(row)

        l0f = [r["f_rmse_mevA"] for r in il_rows if r["lmax"] == "l0"]
        l2f = [r["f_rmse_mevA"] for r in il_rows if r["lmax"] == "l2"]
        l0e = [r["e_rmse_mev"] for r in il_rows if r["lmax"] == "l0"]
        l2e = [r["e_rmse_mev"] for r in il_rows if r["lmax"] == "l2"]
        if l0f and l2f:
            gap_f = np.mean(l0f) - np.mean(l2f)
            gap_e = np.mean(l0e) - np.mean(l2e)
            summary[il] = {
                "anion": ANION_MAP[il],
                "n_seeds": len(seeds),
                "l0_e": round(float(np.mean(l0e)), 1),
                "l2_e": round(float(np.mean(l2e)), 1),
                "l0_f": round(float(np.mean(l0f)), 1),
                "l2_f": round(float(np.mean(l2f)), 1),
                "gap_e": round(float(gap_e), 1),
                "gap_f": round(float(gap_f), 1),
                "energy_gap_paper": ENERGY_GAPS.get(il),
            }
            if len(seeds) > 1:
                summary[il]["l0_f_std"] = round(float(np.std(l0f)), 1)
                summary[il]["l2_f_std"] = round(float(np.std(l2f)), 1)

    # 保存
    out = os.path.join(BASE, "force_8il_comparison.json")
    with open(out, "w") as fh:
        json.dump({"results": all_rows, "summary": summary}, fh, indent=2)
    print(f"\nresults -> {out}", flush=True)

    # 打印 8-IL 排序表（按 force gap 降序）
    if summary:
        print(f"\n{'='*80}", flush=True)
        print(f"{'IL':12s} {'anion':5s} {'l0_F':>10s} {'l2_F':>10s} "
              f"{'gap_F':>10s} {'gap_E(paper)':>12s} {'n_seed':>6s}", flush=True)
        print(f"{'-'*80}", flush=True)
        sorted_ils = sorted(summary.items(), key=lambda x: -x[1]["gap_f"])
        for il, s in sorted_ils:
            print(f"{il:12s} {s['anion']:5s} {s['l0_f']:10.1f} {s['l2_f']:10.1f} "
                  f"{s['gap_f']:+10.1f} {s.get('energy_gap_paper',0):+12.1f} "
                  f"{s['n_seeds']:6d}", flush=True)

        # 对比分析
        print(f"\n{'='*80}", flush=True)
        print("Complexity dependence comparison (energy vs force):", flush=True)
        for il, s in sorted_ils:
            eg = s.get("energy_gap_paper", 0)
            fg = s["gap_f"]
            sign_match = "SAME" if (eg > 0) == (fg > 0) else "OPPOSITE"
            print(f"  {il:12s}: energy_gap={eg:+.1f}, force_gap={fg:+.1f} -> {sign_match}",
                  flush=True)


if __name__ == "__main__":
    main()
