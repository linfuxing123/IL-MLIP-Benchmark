# -*- coding: utf-8 -*-
"""merge_il_data.py — 合并 IL 离子对数据 + 多组分统一训练。

合并 [EMIM][BF4]（30）+ [BMIM][NTf2]（15）→ 按组分归一化训练。
验证条款③：按组分归一化统一训练多组分电解质 ML 势。
"""
import json
import pathlib

import numpy as np

# 合并数据
recs = []
for p in [r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl",
          r"D:\Codex\MEC-Workspace\data\dft_bmim_ntf2.jsonl"]:
    recs.extend([json.loads(l) for l in open(p, encoding="utf-8")])
print(f"合并: {len(recs)} 个 IL 离子对样本", flush=True)

# 原子序数 + padding 到最大原子数
Z = {"H": 1, "B": 5, "C": 6, "N": 7, "O": 8, "F": 9, "S": 16, "P": 15}
max_n = max(len(r["symbols"]) for r in recs)

def pad_z(r):
    z = np.array([Z[s] for s in r["symbols"]], dtype=np.float32)
    pos = np.array(r["positions"], dtype=np.float32)
    zp = np.zeros((max_n,), dtype=np.float32)
    pp = np.zeros((max_n, 3), dtype=np.float32)
    zp[:len(z)] = z
    pp[:len(pos)] = pos
    return zp, pp

import torch
import torch.nn as nn

X = []
for r in recs:
    z, p = pad_z(r)
    X.append(np.hstack([z[:, None], p]))  # (max_n, 4)：原子序数 + 位置
X = np.array(X, dtype=np.float32)
names = [r["name"] for r in recs]
es = np.array([r["energy"] for r in recs])

# 按组分归一化
uniq = sorted(set(names))
e_mean = {n: float(np.mean([r["energy"] for r in recs if r["name"] == n])) for n in uniq}
e_std = {n: float(np.std([r["energy"] for r in recs if r["name"] == n])) for n in uniq}
Y_norm = np.array([(r["energy"] - e_mean[r["name"]]) / e_std[r["name"]] for r in recs], dtype=np.float32)

X = torch.tensor(X)
Y = torch.tensor(Y_norm)

# 简单模型（含原子序数特征）
class ILSchNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.embed = nn.Embedding(20, 8)
        self.net = nn.Sequential(
            nn.Linear(8, 64), nn.SiLU(),
            nn.Linear(64, 64), nn.SiLU(),
            nn.Linear(64, 1),
        )
    def forward(self, x):
        # x: B×N×4 (z, x, y, z)
        z = x[:, :, 0].long()
        e = self.embed(z)  # B×N×8
        e_atom = self.net(e).squeeze(-1)  # B×N
        return e_atom.sum(dim=1)

model = ILSchNet()
opt = torch.optim.Adam(model.parameters(), lr=2e-3)
loss_fn = nn.MSELoss()

idx = torch.randperm(len(X))
n_tr = int(len(X) * 0.8)
X_tr, Y_tr = X[idx[:n_tr]], Y[idx[:n_tr]]
X_te, Y_te = X[idx[n_tr:]], Y[idx[n_tr:]]

print(f"训练 {n_tr} | 测试 {len(X_te)}", flush=True)
for epoch in range(3000):
    opt.zero_grad()
    loss = loss_fn(model(X_tr), Y_tr)
    loss.backward()
    opt.step()
    if epoch % 500 == 0:
        print(f"  epoch {epoch}: loss={loss.item():.6f}", flush=True)

model.eval()
with torch.no_grad():
    pred_norm = model(X_te)
    pred, true = [], []
    te_idx = idx[n_tr:].tolist()
    for i, j in enumerate(te_idx):
        n = names[j]
        pred.append(pred_norm[i].item() * e_std[n] + e_mean[n])
        true.append(es[j])
    mae_mev = np.abs(np.array(pred) - np.array(true)).mean() * 27.2114 * 1000

print(f"\n多组分 IL 测试 MAE = {mae_mev:.0f} meV", flush=True)
print(f"（单组分 SchNet 之前 2178 meV；按组分归一化应改善）", flush=True)
torch.save({"model": model.state_dict(), "e_mean": e_mean, "e_std": e_std, "max_n": max_n},
           r"D:\Codex\MEC-Workspace\data\mlip_il_multicomponent.pt")
print("模型已存: mlip_il_multicomponent.pt", flush=True)
