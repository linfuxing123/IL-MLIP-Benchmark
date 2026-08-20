# -*- coding: utf-8 -*-
"""wsl_force_gen_single.py — WSL PySCF 为单个 IL 生成力（并行用）。
用法: python3 wsl_force_gen_single.py <IL名>
"""
import json, os, time, sys

BOHR_TO_A = 0.5291772109
HA_TO_EV = 27.211386245988
F_CONV = HA_TO_EV / BOHR_TO_A

SRC = "/mnt/d/Codex/MEC-Workspace/data/il_benchmark_clean"
DST = "/mnt/d/Codex/MEC-Workspace/data/il_force"
os.makedirs(DST, exist_ok=True)

IL = sys.argv[1] if len(sys.argv) > 1 else "Pyr14-FSI"


def energy_force(symbols, positions):
    from pyscf import gto, dft
    atom = [(s, (float(x), float(y), float(z)))
            for s, (x, y, z) in zip(symbols, positions)]
    mol = gto.M(atom=atom, basis="sto-3g", verbose=0)
    mf = dft.RKS(mol)
    mf.xc = "b3lyp"
    e = mf.kernel()
    grad = mf.nuc_grad_method().kernel()
    return e, -grad


def write_xyz(path, recs_with_ef):
    lines = []
    for rec, e_ev, f_evA in recs_with_ef:
        n = len(rec["symbols"])
        hdr = (f'energy={e_ev:.10f} config_type=IL_pair name={rec["name"]} '
               f'Properties=species:S:1:pos:R:3:forces:R:3')
        lines.append(str(n))
        lines.append(hdr)
        for s, p, f in zip(rec["symbols"], rec["positions"], f_evA):
            lines.append(f"{s} {p[0]:.10f} {p[1]:.10f} {p[2]:.10f} "
                         f"{f[0]:.10f} {f[1]:.10f} {f[2]:.10f}")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")


def write_jsonl(path, recs_with_ef):
    with open(path, "w", encoding="utf-8") as fh:
        for rec, e_ev, f_evA in recs_with_ef:
            fh.write(json.dumps({
                "id": rec["id"], "name": rec["name"],
                "symbols": rec["symbols"], "positions": rec["positions"],
                "energy_ev": e_ev, "energy_ha": rec.get("energy"),
                "forces_evA": f_evA.tolist(),
                "method": "b3lyp/sto-3g/pyscf",
            }) + "\n")


src = os.path.join(SRC, f"{IL}.jsonl")
xyz_out = os.path.join(DST, f"{IL}_force.xyz")
jsonl_out = os.path.join(DST, f"{IL}_force.jsonl")
recs = [json.loads(l) for l in open(src, encoding="utf-8") if l.strip()]
n = len(recs)
natoms = len(recs[0]["symbols"])

# 幂等 + 断点续传
skip = 0
if os.path.exists(xyz_out):
    txt = open(xyz_out, encoding="utf-8").read().strip().split("\n")
    nframes = len(txt) // (natoms + 2)
    if nframes == n:
        print(f"[SKIP] {IL}: 已有 {nframes}/{n} 帧", flush=True)
        sys.exit(0)
    elif nframes > 0:
        skip = nframes
        print(f"[RESUME] {IL}: 已有 {nframes}/{n} 帧，从第 {skip} 帧继续", flush=True)

print(f"[START] {IL}: {n} conf, {natoms} atoms (skip {skip})", flush=True)
t0 = time.time()
good = []
nfail = 0
for i, r in enumerate(recs):
    if i < skip:
        continue
    try:
        e_ha, f_hab = energy_force(r["symbols"], r["positions"])
        e_ev = e_ha * HA_TO_EV
        f_evA = f_hab * F_CONV
        r2 = dict(r); r2["name"] = IL
        good.append((r2, e_ev, f_evA))
    except Exception as ex:
        nfail += 1
        with open(os.path.join(DST, "failed.txt"), "a", encoding="utf-8") as fh:
            fh.write(f"{IL}\tconf{i}\t{type(ex).__name__}: {ex}\n")
    if (i + 1) % 5 == 0 or (i + 1) == n:
        dt = time.time() - t0
        print(f"  {IL} {i+1}/{n} ok={len(good)} fail={nfail} "
              f"elapsed={dt:.0f}s rate={dt/(i+1):.1f}s/conf", flush=True)
        if good:
            write_xyz(xyz_out, good)
            write_jsonl(jsonl_out, good)
write_xyz(xyz_out, good)
write_jsonl(jsonl_out, good)
dt = time.time() - t0
print(f"[DONE] {IL}: {len(good)}/{n} ok, {nfail} fail, {dt:.0f}s", flush=True)
