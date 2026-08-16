# -*- coding: utf-8 -*-
"""learning_curve.py — 学习曲线：MAE 随训练样本量的变化。

关键实验：验证 IL 离子对 ML 势需要多少数据。
用已有数据（295 样本）+ 批量生成中的，按不同训练量重训，看 MAE 收敛。
"""
import json
import pathlib

import numpy as np
import torch
import torch.nn as nn

torch.manual_seed(42)

# 合并所有 IL 数据（含 batch 已生成的）
def load_all():
    files = [
        r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl",
        r"D:\Codex\MEC-Workspace\data\dft_bmim_ntf2.jsonl",
        r"D:\Codex\MEC-Workspace\data\dft_il_batch.jsonl",
    ]
    recs = []
    for p in files:
        fp = pathlib.Path(p)
        if fp.exists():
            try:
                recs.extend([json.loads(l) for l in fp.open(encoding="utf-8")])
            except Exception:
                pass
    return recs

recs = load_all()
print(f"当前 IL 数据: {len(recs)} 样本", flush=True)

if len(recs) < 40:
    print("数据不足 40，等批量生成更多后再跑学习曲线", flush=True)
    exit(0)

max_n = max(len(r["symbols"]) for r in recs)
def pad(r):
    pos = np.array(r["positions"], dtype=np.float32)
    pp = np.zeros((max_n, 3), dtype=np.float32)
    pp[:len(pos)] = pos
    return pp

X = torch.tensor(np.array([pad(r) for r in recs], dtype=np.float32))
names = [r["name"] for r in recs]
es = np.array([r["energy"] for r in recs])

# 按组分归一化
uniq = sorted(set(names))
e_mean = {n: float(np.mean([r["energy"] for r in recs if r["name"] == n])) for n in uniq}
e_std = {n: float(np.std([r["energy"] for r in recs if r["name"] == n])) or 1.0 for n in uniq}
Y = torch.tensor(np.array([(r["energy"] - e_mean[r["name"]]) / e_std[r["name"]] for r in recs], dtype=np.float32))

class ILSchNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.mu = torch.linspace(0.5, 6.0, 48)
        self.sigma = 0.18
        self.net = nn.Sequential(
            nn.Linear(48, 96), nn.SiLU(), nn.Linear(96, 96), nn.SiLU(), nn.Linear(96, 1))
    def forward(self, pos):
        B, N, _ = pos.shape
        d = torch.norm(pos[:, :, None, :] - pos[:, None, :, :], dim=-1)
        g = torch.exp(-((d.unsqueeze(-1) - self.mu) / self.sigma) ** 2)
        mask = torch.eye(N, dtype=torch.bool)
        g = g * (~mask).view(1, N, N, 1)
        feat = g.sum(dim=2)
        return self.net(feat).squeeze(-1).sum(dim=1)

# 学习曲线：不同训练量
print("\n=== 学习曲线（MAE vs 训练样本量）===")
for frac in [0.4, 0.6, 0.8]:
    n_tr = int(len(X) * frac)
    idx = torch.randperm(len(X))
    X_tr, Y_tr = X[idx[:n_tr]], Y[idx[:n_tr]]
    X_te, Y_te = X[idx[n_tr:]], Y[idx[n_tr:]]
    model = ILSchNet()
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    for _ in range(2000):
        opt.zero_grad()
        loss = nn.MSELoss()(model(X_tr), Y_tr)
        loss.backward()
        opt.step()
    model.eval()
    with torch.no_grad():
        pred = model(X_te)
        mae = 0.0
        te_idx = idx[n_tr:].tolist()
        for i, j in enumerate(te_idx):
            n = names[j]
            mae += abs(pred[i].item() * e_std[n] + e_mean[n] - es[j])
        mae_mev = (mae / len(te_idx)) * 27.2114 * 1000
    print(f"  训练 {n_tr} 样本 → 测试 MAE {mae_mev:.0f} meV", flush=True)

print("\n（观察 MAE 是否随数据量下降——验证数据规模需求）", flush=True)
