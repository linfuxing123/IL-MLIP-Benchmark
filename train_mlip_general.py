# -*- coding: utf-8 -*-
"""train_mlip_general.py — 通用 ML 势训练器（多分子，供 agent 调用）。

用法：python train_mlip_general.py <data.jsonl> [--out model.pt] [--epochs 2000]
数据：JSONL，每行 {symbols, positions, energy}
输出：模型 + 评估（能量 MAE，meV）
"""
import argparse
import json
import pathlib

import numpy as np
import torch
import torch.nn as nn

class SchNetInvariant(nn.Module):
    def __init__(self, n_gauss=32, hidden=64):
        super().__init__()
        self.n_gauss = n_gauss
        self.mu = torch.linspace(0.5, 2.5, n_gauss)  # 覆盖多分子键长
        self.sigma = 0.08
        self.net = nn.Sequential(
            nn.Linear(n_gauss, hidden), nn.SiLU(),
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
        feat = g.sum(dim=2)
        e_atom = self.net(feat).squeeze(-1)
        return e_atom.sum(dim=1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", help="JSONL 数据路径")
    ap.add_argument("--out", default=r"D:\Codex\MEC-Workspace\data\mlip_general.pt")
    ap.add_argument("--epochs", type=int, default=2000)
    ap.add_argument("--max-atoms", type=int, default=5)
    args = ap.parse_args()

    # 加载数据（对齐原子数，按最大原子数 padding）
    recs = [json.loads(l) for l in open(args.data, encoding="utf-8")]
    max_n = max(len(r["positions"]) for r in recs)
    print(f"数据: {len(recs)} 样本, 最大原子数 {max_n}", flush=True)

    def pad(pos, n):
        arr = np.zeros((n, 3), dtype=np.float32)
        arr[:len(pos)] = pos
        return arr

    positions = np.array([pad(r["positions"], max_n) for r in recs], dtype=np.float32)
    energies = np.array([r["energy"] for r in recs])

    # 按分子（name 字段）归一化：各自减均值/除标准差，避免跨分子绝对能量尺度差异
    names = [r.get("name", "mol") for r in recs]
    uniq = sorted(set(names))
    per_mol = {n: np.array([r["energy"] for r in recs if r.get("name", "mol") == n]) for n in uniq}
    e_mean = {n: float(es.mean()) for n, es in per_mol.items()}
    e_std = {n: (float(es.std()) if es.std() > 1e-8 else 1.0) for n, es in per_mol.items()}
    Y_norm = np.array([(r["energy"] - e_mean[n]) / e_std[n] for r, n in zip(recs, names)], dtype=np.float32)

    X = torch.tensor(positions)
    Y = torch.tensor(Y_norm)

    model = SchNetInvariant()
    opt = torch.optim.Adam(model.parameters(), lr=2e-3)
    loss_fn = nn.MSELoss()

    idx = torch.randperm(len(X))
    n_tr = int(len(X) * 0.8)
    X_tr, Y_tr = X[idx[:n_tr]], Y[idx[:n_tr]]
    X_te, Y_te = X[idx[n_tr:]], Y[idx[n_tr:]]

    for epoch in range(args.epochs):
        opt.zero_grad()
        loss = loss_fn(model(X_tr), Y_tr)
        loss.backward()
        opt.step()
        if epoch % 400 == 0:
            print(f"  epoch {epoch}: loss={loss.item():.6f}", flush=True)

    model.eval()
    with torch.no_grad():
        # 按分子还原能量
        pred_norm = model(X_te)
        pred = []
        true = []
        te_idx = idx[n_tr:].tolist()
        for i, j in enumerate(te_idx):
            n = names[j]
            pred.append(pred_norm[i].item() * e_std[n] + e_mean[n])
            true.append(energies[j])
        pred = np.array(pred)
        true = np.array(true)
        mae_mev = np.abs(pred - true).mean() * 27.2114 * 1000

    print(f"\n测试 MAE = {mae_mev:.1f} meV", flush=True)
    print("✅ 达到化学精度" if mae_mev < 43 else "⚠️ 需更多数据/更久训练", flush=True)

    torch.save({"model": model.state_dict(), "e_mean": e_mean, "e_std": e_std,
                "max_atoms": max_n}, args.out)
    print(f"模型已存: {args.out}", flush=True)

if __name__ == "__main__":
    main()
