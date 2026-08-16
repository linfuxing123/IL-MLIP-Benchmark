# -*- coding: utf-8 -*-
"""record_il_mlip.py — IL-MLIP-Benchmark 成果入 mec.db。"""
import subprocess

# 论文记录
cmd1 = [
    "D:/Codex/.cache/codex-runtimes/mec-lit-venv/Scripts/python.exe",
    "D:/Codex/MEC-Workspace/data/mec_db.py", "add-paper",
    "--doi", "il-mlip-benchmark-2026",
    "--title", "IL-MLIP-Benchmark: A Benchmark Dataset and Energy-Decomposition Analysis for Ionic Liquid Machine-Learned Interatomic Potentials",
    "--title-cn", "IL-MLIP-Benchmark：离子液体机器学习势的基准数据集与能量分解分析",
    "--journal", "准备投稿（Scientific Data / Digital Discovery）",
    "--authors", "Lin, Fuxing",
    "--published", "2026-08-16",
    "--notes", "首个系统性 IL 离子对 MLIP 基准数据集（8 IL × 205 干净构型）。MACE 微调达化学精度 23.3 meV/atom（5 折交叉验证），比 SchNet 从头训练（6115.7 meV）好 263 倍。EDT 能量分解：离子刚性（E_cat 54/E_an 14 meV）+ 可迁移性。",
]
r1 = subprocess.run(cmd1, capture_output=True, text=True)
print("paper:", r1.stdout.strip() or r1.stderr.strip())

# 成果记录
cmd2 = [
    "D:/Codex/.cache/codex-runtimes/mec-lit-venv/Scripts/python.exe",
    "D:/Codex/MEC-Workspace/data/mec_db.py", "add-achievement",
    "--paper", "il-mlip-benchmark-2026",
    "--date", "2026-08-16",
    "--category", "论文",
    "--title", "IL 离子对 MLIP 达化学精度（23.3 meV/atom）",
    "--summary", "MACE 微调 EMIM-BF4 达化学精度 23.3 meV/atom（5 折交叉验证），比 SchNet 从头训练 6115.7 meV 好 263 倍。EDT 能量分解验证离子刚性（E_cat 54/E_an 14 meV）+ 可迁移性。数据：8 IL 205 干净构型（B3LYP/STO-3G，过滤原子重叠坏构型）。",
    "--highlights", "化学精度23.3meV|预训练263倍优势|EDT离子刚性|8IL基准数据集|5折交叉验证",
    "--status", "完成",
]
r2 = subprocess.run(cmd2, capture_output=True, text=True)
print("achievement:", r2.stdout.strip() or r2.stderr.strip())
