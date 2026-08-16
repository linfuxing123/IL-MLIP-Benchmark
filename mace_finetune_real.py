# -*- coding: utf-8 -*-
"""mace_finetune_real.py — MACE-MP-0 全参数微调到 IL 数据。

用 MACE 底层模型（ScaleShiftMACE，384 万参数），在 [EMIM][BF4] 数据上
全参数微调（小学习率，保留预训练先验）。
"""
import json
import pathlib

import numpy as np
import torch

DATA = pathlib.Path(r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl")
MODEL = r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model"
recs = [json.loads(l) for l in DATA.open(encoding="utf-8")]

from mace.calculators import mace_mp
from ase import Atoms
from mace.data.utils import config_from_atoms
from mace.data import AtomicData  # 可能用到

# 加载底层模型
model = mace_mp(model=MODEL, return_raw_model=True, default_dtype="float64", device="cpu")
print(f"模型: {type(model).__name__}, {sum(p.numel() for p in model.parameters()):,} 参数", flush=True)

# 构造输入 data dict（用 config_from_atoms → AtomicData → torch_geometric data）
def atoms_to_data(symbols, positions):
    from mace.data.utils import config_from_atoms, AtomicNumberTable
    atoms = Atoms(symbols=symbols, positions=positions)
    config = config_from_atoms(atoms)
    z_table = AtomicNumberTable(list(range(1, 90)))  # 默认全元素表（89 元素）
    from mace.data.atomic_data import AtomicData
    atomic = AtomicData.from_config(config, z_table=z_table, cutoff=6.0)
    d = atomic.to_dict()
    # 单图：补 batch/head（全 0）和 ptr（[0, n]）
    n = len(d["positions"])
    d["batch"] = torch.zeros(n, dtype=torch.long)
    d["head"] = torch.zeros(n, dtype=torch.long)
    d["ptr"] = torch.tensor([0, n], dtype=torch.long)
    return d

print("构造数据...", flush=True)
datas = [atoms_to_data(r["symbols"], r["positions"]) for r in recs]
e_dft = torch.tensor([r["energy"] * 27.2114 for r in recs], dtype=torch.float64)  # eV

# 微调：小学习率，全参数
opt = torch.optim.Adam(model.parameters(), lr=1e-5)
loss_fn = torch.nn.MSELoss()

n = len(recs)
idx = torch.randperm(n)
n_tr = int(n * 0.8)
tr, te = idx[:n_tr].tolist(), idx[n_tr:].tolist()

print(f"微调 {len(tr)} | 测试 {len(te)}", flush=True)
for epoch in range(200):
    opt.zero_grad()
    loss = 0.0
    for i in tr:
        out = model(datas[i], training=True, compute_force=False)
        e = out["energy"]  # (1,1) 或标量
        loss = loss + loss_fn(e.reshape(-1)[0], e_dft[i])
    loss = loss / len(tr)
    loss.backward()
    opt.step()
    if epoch % 40 == 0:
        print(f"  epoch {epoch}: loss={loss.item():.4f}", flush=True)

# 评估
model.eval()
preds, trues = [], []
with torch.no_grad():
    for i in te:
        out = model(datas[i], training=False, compute_force=False)
        preds.append(out["energy"].reshape(-1)[0].item())
        trues.append(e_dft[i].item())
mae = np.abs(np.array(preds) - np.array(trues)).mean() * 1000
print(f"\n微调后测试 MAE = {mae:.1f} meV", flush=True)
print(f"{'✅ 达到化学精度！' if mae < 43 else '接近，需更多数据'}", flush=True)
