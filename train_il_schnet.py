# -*- coding: utf-8 -*-
"""train_il_schnet.py — 修正版：距离高斯特征的 IL 离子对 ML 势。

修正上一轮 bug：加回距离高斯扩展（几何感知），按组分归一化。
数据：[EMIM][BF4] 30 + [BMIM][NTf2] 15
"""
import json
import pathlib

import numpy as np
import torch
import torch.nn as nn

torch.manual_seed(42)

recs = []
for p in [r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl",
          r"D:\Codex\MEC-Workspace\data\dft_bmim_ntf2.jsonl"]:
    recs.extend([json.loads(l) for l in open(p, encoding="utf-8")])
print(f"合并: {len(recs)} 个 IL 离子对", flush=True)

max_n = max(len(r["symbols"]) for r in recs)

def pad(r):
    pos = np.array(r["positions"], dtype=np.float32)
    pp = np.zeros((max_n, 3), dtype=np.float32)
    pp[:len(pos)] = pos
    return pp

X = np.array([pad(r) for r in recs], dtype=np.float32)
names = [r["name"] for r in recs]
es = np.array([r["energy"] for r in recs])

uniq = sorted(set(names))
e_mean = {n: float(np.mean([r["energy"] for r in recs if r["name"] == n])) for n in uniq}
e_std = {n: float(np.std([r["energy"] for r in recs if r["name"] == n])) or 1.0 for n in uniq}
Y = np.array([(r["energy"] - e_mean[r["name"]]) / e_std[r["name"]] for r in recs], dtype=np.float32)

X = torch.tensor(X)
Y = torch.tensor(Y)

class ILDistSchNet(nn.Module):
    def __init__(self, n_gauss=64, hidden=128):
        super().__init__()
        self.n_gauss = n_gauss
        self.mu = torch.linspace(0.5, 6.0, n_gauss)  # 覆盖 IL 离子对距离范围
        self.sigma = 0.15
        self.net = nn.Sequential(
            nn.Linear(n_gauss, hidden), nn.SiLU(),
            nn.Linear(hidden, hidden), nn.SiLU(),
            nn.Linear(hidden, hidden), nn.SiLU(),
            nn.Linear(hidden, 1),
        )
    def forward(self, pos):
        B, N, _ = pos.shape
        diff = pos[:, :, None, :] - pos[:, None, :, :]
        d = torch.norm(diff, dim=-1)
        g = torch.exp(-((d.unsqueeze(-1) - self.mu) / self.sigma) ** 2)
        mask = torch.eye(N, dtype=torch.bool)
        g = g * (~mask).view(1, N, N, 1)
        feat = g.sum(dim=2)  # B×N×G
        e_atom = self.net(feat).squeeze(-1)
        return e_atom.sum(dim=1)

model = ILDistSchNet()
opt = torch.optim.Adam(model.parameters(), lr=1e-3)
loss_fn = nn.MSELoss()

idx = torch.randperm(len(X))
n_tr = int(len(X) * 0.8)
X_tr, Y_tr = X[idx[:n_tr]], Y[idx[:n_tr]]
X_te, Y_te = X[idx[n_tr:]], Y[idx[n_tr:]]

print(f"训练 {n_tr} | 测试 {len(X_te)}", flush=True)
for epoch in range(4000):
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

print(f"\nIL 离子对测试 MAE = {mae_mev:.0f} meV", flush=True)
print(f"（目标 < 43 meV；数据 {len(recs)} 样本）", flush=True)
torch.save({"model": model.state_dict(), "e_mean": e_mean, "e_std": e_std, "max_n": max_n},
           r"D:\Codex\MEC-Workspace\data\mlip_il_schnet.pt")
print("模型已存: mlip_il_schnet.pt", flush=True)
