# -*- coding: utf-8 -*-
"""train_h2o_mlip.py — 用真实 DFT 数据训练 H2O ML 势。

数据：data/dft_h2o.jsonl（50 个 H2O 几何 × B3LYP/STO-3G 能量）
模型：SchNet 风格（高斯距离扩展 + MLP，秩不变）
任务：拟合能量（目标：相对能量误差 << 化学精度 1 kcal/mol = 43 meV）
"""
import json
import pathlib

import numpy as np
import torch
import torch.nn as nn

torch.manual_seed(42)
device = torch.device("cpu")  # 小数据 CPU 更快

# ── 1. 加载数据 ────────────────────────────────────────────────
DATA = pathlib.Path(r"D:\Codex\MEC-Workspace\data\dft_h2o.jsonl")
recs = [json.loads(l) for l in DATA.open(encoding="utf-8")]
print(f"数据: {len(recs)} 个 H2O 几何", flush=True)

# 能量归一化（减去均值，便于学习）
energies = np.array([r["energy"] for r in recs])
e_mean = energies.mean()
e_std = energies.std()
print(f"能量: 均值 {e_mean:.4f} Ha, 标准差 {e_std*1000:.2f} mHa", flush=True)

positions = np.array([r["positions"] for r in recs], dtype=np.float32)  # N×3×3
Y = ((energies - e_mean) / e_std).astype(np.float32)  # 归一化

X = torch.tensor(positions)
Y = torch.tensor(Y)

# ── 2. 模型（SchNet 风格，E(3)-invariant）───────────────────────
class H2OSchNet(nn.Module):
    def __init__(self, n_gauss=32, hidden=64):
        super().__init__()
        self.n_gauss = n_gauss
        # 高斯中心聚焦键长范围 0.5-1.5 Å
        self.mu = torch.linspace(0.5, 1.5, n_gauss)
        self.sigma = 0.05
        self.net = nn.Sequential(
            nn.Linear(n_gauss, hidden), nn.SiLU(),
            nn.Linear(hidden, hidden), nn.SiLU(),
            nn.Linear(hidden, 1),
        )

    def forward(self, pos):
        B, N, _ = pos.shape
        diff = pos[:, :, None, :] - pos[:, None, :, :]
        d = torch.norm(diff, dim=-1)  # B×N×N
        g = torch.exp(-((d.unsqueeze(-1) - self.mu) / self.sigma) ** 2)
        mask = torch.eye(N, dtype=torch.bool)
        g = g * (~mask).view(1, N, N, 1)
        feat = g.sum(dim=2)  # B×N×G
        e_atom = self.net(feat).squeeze(-1)  # B×N
        return e_atom.sum(dim=1)  # B

model = H2OSchNet()
opt = torch.optim.Adam(model.parameters(), lr=2e-3)
loss_fn = nn.MSELoss()

# ── 3. 训练（留一交叉验证式：50 太小，用 40/10 划分）─────────────
idx = torch.randperm(len(X))
n_tr = 40
X_tr, Y_tr = X[idx[:n_tr]], Y[idx[:n_tr]]
X_te, Y_te = X[idx[n_tr:]], Y[idx[n_tr:]]

print(f"训练 {n_tr} | 测试 {len(X_te)}", flush=True)
for epoch in range(2000):
    opt.zero_grad()
    loss = loss_fn(model(X_tr), Y_tr)
    loss.backward()
    opt.step()
    if epoch % 200 == 0:
        print(f"  epoch {epoch}: loss={loss.item():.6f}", flush=True)

# ── 4. 评估（还原到 Ha / mHa）───────────────────────────────────
model.eval()
with torch.no_grad():
    pred_te = model(X_te) * e_std + e_mean
    true_te = Y_te * e_std + e_mean
    mae_ha = (pred_te - true_te).abs().mean().item()
    mae_mev = mae_ha * 27.2114 * 1000  # Hartree → meV

print(f"\n测试 MAE = {mae_ha*1000:.2f} mHa = {mae_mev:.1f} meV", flush=True)
print(f"化学精度阈值 43 meV（1 kcal/mol）:", flush=True)
if mae_mev < 43:
    print("✅ 达到化学精度！", flush=True)
else:
    print(f"❌ 差 {mae_mev/43:.1f} 倍（数据量 50 太少，需扩充）", flush=True)

# 保存模型
torch.save({"model": model.state_dict(), "e_mean": e_mean, "e_std": e_std},
           r"D:\Codex\MEC-Workspace\data\h2o_mlip.pt")
print("模型已存: data\\h2o_mlip.pt", flush=True)
