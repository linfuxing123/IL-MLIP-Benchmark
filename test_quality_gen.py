# -*- coding: utf-8 -*-
"""test_quality_gen.py — 测源头质量保证的生成器（10 个 EMIM-BF4）。"""
import json
import pathlib
import numpy as np

# 直接调用生成逻辑
import importlib.util
spec = importlib.util.spec_from_file_location("pool", r"/mnt/d/Codex/MEC-Workspace/workspace/chem-library/il_benchmark_pool.py")
pool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pool)

name = "EMIM-BF4"
csmi, asmi = pool.ILS[name]
es = []
for i in range(5):
    seed_cat = pool.stable_hash(csmi) + i * 7
    seed_an = pool.stable_hash(asmi) + i * 13
    cs, cp = pool.embed(csmi, seed_cat)
    as_, ap = pool.embed(asmi, seed_an)
    dist = 4.0 + 1.5 * (i % 10) / 9
    rng = np.random.default_rng(seed_cat + seed_an)
    for attempt in range(20):
        d = rng.normal(size=3); d /= np.linalg.norm(d)
        ap_s = ap + d * dist
        cand = np.vstack([cp, ap_s])
        min_d = np.linalg.norm(cand[:len(cs)][:, None, :] - cand[len(cs):][None, :, :], axis=-1).min()
        if min_d >= 2.0:
            symbols = cs + as_
            e, _, _ = pool.energy_force(symbols, cand)
            if e is not None:
                es.append(e)
            break
es = np.array(es)
print(f"EMIM-BF4 测试 {len(es)} 个")
print(f"  能量 {es.min():.4f} ~ {es.max():.4f} Ha, std {es.std()*1000:.0f} mHa")
print(f"  {'✅ 质量好（std < 500 mHa）' if es.std()*1000 < 500 else '⚠️ std 仍偏大'}")
