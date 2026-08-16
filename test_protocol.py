# -*- coding: utf-8 -*-
"""test_protocol.py — 测成功协议（seed=i + 随机距离）质量。"""
import json
import pathlib
import numpy as np

import importlib.util
spec = importlib.util.spec_from_file_location("pool", r"/mnt/d/Codex/MEC-Workspace/workspace/chem-library/il_benchmark_pool.py")
pool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pool)

name = "EMIM-BF4"
csmi, asmi = pool.ILS[name]
es = []
for i in range(10):
    cs, cp = pool.embed(csmi, i)
    as_, ap = pool.embed(asmi, i * 7 + 3)
    symbols = cs + as_
    cat_n = len(cs)
    for attempt in range(30):
        rng = np.random.default_rng(i + attempt * 1000)
        d = rng.normal(size=3); d /= np.linalg.norm(d)
        dist = rng.uniform(3.5, 5.5)
        ap_s = ap + d * dist
        cand = np.vstack([cp, ap_s])
        min_d = np.linalg.norm(cand[:cat_n][:, None, :] - cand[cat_n:][None, :, :], axis=-1).min()
        if min_d >= 1.5:
            e, _, _ = pool.energy_force(symbols, cand)
            if e is not None:
                es.append(e)
            break
es = np.array(es)
print(f"EMIM-BF4 {len(es)} 个")
print(f"  能量 {es.min():.4f} ~ {es.max():.4f} Ha, std {es.std()*1000:.0f} mHa")
print(f"  {'✅ 质量好（std 400-600 mHa 合理）' if 300 < es.std()*1000 < 800 else '⚠️ 检查 std'}")
