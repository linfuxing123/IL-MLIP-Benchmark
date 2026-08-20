# -*- coding: utf-8 -*-
"""force_eval_32ch.py — 评估 32ch l0 vs l2 力模型。

读 32ch 训练好的模型，在 test 集上算 energy/force RMSE。
模型命名: force_<IL>_<l0/l2>_s<seed>_32ch
"""
import os, sys, glob, json
import numpy as np
from ase.io import read
from mace.calculators import MACECalculator

BASE = r"D:\Codex\MEC-Workspace\data\il_force_models"
SPLIT_DIR = r"D:\Codex\MEC-Workspace\data\il_force"
ILS = ["EMIM-BF4", "Pyr14-FSI"]
SEEDS = ["7", "42", "123"]


def eval_model(model_dir, test_file, device="cpu"):
    cand = glob.glob(os.path.join(model_dir, "*_compiled.model"))
    if not cand:
        cand = glob.glob(os.path.join(model_dir, "*.model"))
    if not cand:
        return None, None, 0
    # Use stagetwo_compiled if available (SWA/EMA final model)
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
    for il in ILS:
        test_file = os.path.join(SPLIT_DIR, f"split_{il}", "test_15.xyz")
        if not os.path.exists(test_file):
            print(f"!! {il}: 缺 test 文件", flush=True)
            continue
        print(f"\n=== 评估 {il} (32ch) ===", flush=True)
        il_rows = []
        for lmax in ["l0", "l2"]:
            for seed in SEEDS:
                name = f"force_{il}_{lmax}_s{seed}_32ch"
                md = os.path.join(BASE, il, name)
                e, f, n = eval_model(md, test_file)
                if e is None:
                    print(f"  {name}: 模型缺失", flush=True)
                    continue
                print(f"  {name}: E={e:.1f} meV/atom, F={f:.1f} meV/A (n={n})",
                      flush=True)
                row = {"il": il, "lmax": lmax, "seed": seed, "channels": 32,
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
            print(f"\n  --- {il} (32ch, 3 seed mean+/-std) ---", flush=True)
            print(f"  l0: E={np.mean(l0e):.1f}+/-{np.std(l0e):.1f} meV, "
                  f"F={np.mean(l0f):.1f}+/-{np.std(l0f):.1f} meV/A", flush=True)
            print(f"  l2: E={np.mean(l2e):.1f}+/-{np.std(l2e):.1f} meV, "
                  f"F={np.mean(l2f):.1f}+/-{np.std(l2f):.1f} meV/A", flush=True)
            print(f"  delta_E(l0-l2) = {gap_e:+.1f} meV", flush=True)
            print(f"  delta_F(l0-l2) = {gap_f:+.1f} meV/A  "
                  f"({'equivariant better' if gap_f > 0 else 'scalar better/no advantage'})",
                  flush=True)
            summary[il] = {
                "l0_e_mean": round(float(np.mean(l0e)), 1),
                "l0_e_std": round(float(np.std(l0e)), 1),
                "l0_f_mean": round(float(np.mean(l0f)), 1),
                "l0_f_std": round(float(np.std(l0f)), 1),
                "l2_e_mean": round(float(np.mean(l2e)), 1),
                "l2_e_std": round(float(np.std(l2e)), 1),
                "l2_f_mean": round(float(np.mean(l2f)), 1),
                "l2_f_std": round(float(np.std(l2f)), 1),
                "gap_e": round(float(gap_e), 1),
                "gap_f": round(float(gap_f), 1),
            }

    out = os.path.join(BASE, "force_32ch_comparison.json")
    with open(out, "w") as fh:
        json.dump({"results": all_rows, "summary": summary}, fh, indent=2)
    print(f"\n=== 对比结果 ===\nresults -> {out}", flush=True)

    if "EMIM-BF4" in summary and "Pyr14-FSI" in summary:
        s1 = summary["EMIM-BF4"]
        s2 = summary["Pyr14-FSI"]
        print(f"\n{'IL':12s} {'delta_E':>10s} {'delta_F':>10s} {'verdict':>25s}", flush=True)
        v1 = "equivariant better" if s1["gap_f"] > 0 else "scalar/no advantage"
        v2 = "equivariant better" if s2["gap_f"] > 0 else "scalar/no advantage"
        print(f"{'EMIM-BF4':12s} {s1['gap_e']:+10.1f} {s1['gap_f']:+10.1f} {v1:>25s}", flush=True)
        print(f"{'Pyr14-FSI':12s} {s2['gap_e']:+10.1f} {s2['gap_f']:+10.1f} {v2:>25s}", flush=True)
        complexity_confirmed = (s1["gap_f"] <= 0 < s2["gap_f"])
        print(f"\nComplexity-dependence in forces: "
              f"{'CONFIRMED' if complexity_confirmed else 'see detailed results'}", flush=True)


if __name__ == "__main__":
    main()
