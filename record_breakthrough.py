# -*- coding: utf-8 -*-
"""record_breakthrough.py — MACE 突破成果入 mec.db。"""
import subprocess

cmd = [
    "D:/Codex/.cache/codex-runtimes/mec-lit-venv/Scripts/python.exe",
    "D:/Codex/MEC-Workspace/data/mec_db.py", "add-achievement",
    "--paper", "mlip-electrolyte-2026",
    "--date", "2026-08-16",
    "--category", "论文",
    "--title", "MACE 预训练突破：IL 离子对微调逼近化学精度（57.3 meV/atom）",
    "--summary", "突破 MACE 权重下载（gh-proxy 镜像）；MACE-MP-0 zero-shot corr 0.994；微调（45 样本 20 epoch）验证 RMSE 57.3 meV/atom 逼近化学精度 43 meV。对比 SchNet 从头训练（万级 meV）质变。方法学：多组分必须按组分归一化（152 样本 4 IL 混合 716.7 meV 反证）。数据库扩充至 911 文献 + 667 PDF + 165 IL DFT 数据。",
    "--highlights", "MACE权重突破(ghproxy)|zero-shot corr 0.994|微调57.3meV逼近化学精度|多组分归一化|数据库911+",
    "--status", "进行中",
]
r = subprocess.run(cmd, capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
