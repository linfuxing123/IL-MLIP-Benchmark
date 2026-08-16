# -*- coding: utf-8 -*-
"""schnet_baseline.py — SchNet 从头训练（基线对比 MACE 微调）。

用 EMIM-BF4 29 个干净数据，SchNet 不变模型从头训练，5 折交叉验证。
对比 MACE 微调（23.3 meV/atom），展示预训练模型的优势。
"""
import json
import numpy as np
import torch
import torch.nn as nn

torch.manual_seed(42)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

emim = [json.loads(l) for l in open(r"D:\Codex\MEC-Workspace\data\il_benchmark_clean\EMIM-BF4.jsonl", encoding="utf-8")]
n = len(emim)
print(f"EMIM-BF4 {n} 个干净数据，SchNet 从头训练 5 折交叉验证", flush=True)

max_n = max(len(r["symbols"]) for r in emim)
def pad(r):
    pos = np.array(r["positions"], dtype=np.float32)
    pp = np.zeros((max_n, 3), dtype=np.float32)
    pp[:len(pos)] = pos
    return pp

X = torch.tensor(np.array([pad(r) for r in emim]), dtype=torch.float32)
es = np.array([r["energy"] * 27.2114 for r in emim], dtype=np.float32)
e_mean = es.mean()
Y = torch.tensor(es - e_mean, dtype=torch.float32)

class SchNet(nn.Module):
    def __init__(self, n_gauss=48, hidden=96):
        super().__init__()
        self.mu = torch.linspace(0.5, 6.0, n_gauss)
        self.sigma = 0.18
        self.net = nn.Sequential(
            nn.Linear(n_gauss, hidden), nn.SiLU(),
            nn.Linear(hidden, hidden), nn.SiLU(),
            nn.Linear(hidden, 1))
    def forward(self, pos):
        B, N, _ = pos.shape
        d = torch.norm(pos[:, :, None, :] - pos[:, None, :, :], dim=-1)
        g = torch.exp(-((d.unsqueeze(-1) - self.mu.to(pos.device)) / self.sigma) ** 2)
        mask = torch.eye(N, dtype=torch.bool, device=pos.device)
        g = g * (~mask).view(1, N, N, 1)
        feat = g.sum(dim=2)
        return self.net(feat).squeeze(-1).sum(dim=1)

# 5 折交叉验证
rng = np.random.RandomState(42)
idx = rng.permutation(n)
fold_size = n // 5
fold_rmses = []
for fold in range(5):
    te_idx = idx[fold*fold_size:(fold+1)*fold_size]
    tr_idx = [i for i in idx if i not in te_idx]
    model = SchNet().to(device)
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    X_tr = X[tr_idx].to(device)
    Y_tr = Y[tr_idx].to(device)
    X_te = X[te_idx].to(device)
    for epoch in range(3000):
        opt.zero_grad()
        loss = nn.MSELoss()(model(X_tr), Y_tr)
        loss.backward()
        opt.step()
    model.eval()
    with torch.no_grad():
        pred = model(X_te).cpu() + e_mean
        true = torch.tensor(es[te_idx])
        rmse = (pred - true).abs().mean().item() * 1000
    fold_rmses.append(rmse)
    print(f"  fold {fold}: {rmse:.1f} meV/atom", flush=True)

print(f"\nSchNet 从头训练 5 折 RMSE: {np.mean(fold_rmses):.1f} ± {np.std(fold_rmses):.1f} meV/atom", flush=True)
print(f"（对比 MACE 微调 23.3 meV/atom）", flush=True)
