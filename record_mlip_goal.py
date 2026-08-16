# -*- coding: utf-8 -*-
"""record_mlip_goal.py — 电解质 ML 势成果入 mec.db。"""
import subprocess

# 1. 论文记录（探索性方法学研究）
cmd1 = [
    "D:/Codex/.cache/codex-runtimes/mec-lit-venv/Scripts/python.exe",
    "D:/Codex/MEC-Workspace/data/mec_db.py", "add-paper",
    "--doi", "mlip-electrolyte-2026",
    "--title", "From molecules to ionic liquids: scaling limits of machine-learned interatomic potentials",
    "--title-cn", "电解质 ML 势方法学：从分子到离子液体的数据规模限制",
    "--journal", "探索性研究（内部报告）",
    "--authors", "Lin, Fuxing",
    "--published", "2026-08-16",
    "--notes", "小分子/带电离子 ML 势达化学精度（H2O 22.8/多分子 0.3/离子 3.3 meV）；IL 离子对受数据规模限制（51 样本过拟合，需数百）。方法学：按组分归一化能量（1700 倍提升）、RDKit 构型必需、等变模型必要。",
]
r1 = subprocess.run(cmd1, capture_output=True, text=True)
print("paper:", r1.stdout.strip() or r1.stderr.strip())

# 2. 成果记录
cmd2 = [
    "D:/Codex/.cache/codex-runtimes/mec-lit-venv/Scripts/python.exe",
    "D:/Codex/MEC-Workspace/data/mec_db.py", "add-achievement",
    "--paper", "mlip-electrolyte-2026",
    "--date", "2026-08-16",
    "--category", "论文",
    "--title", "电解质 ML 势全链路 + 方法学结论",
    "--summary", "PySCF(WSL) 生成 DFT 数据（455 样本：H2O/多分子/离子/IL 离子对）→ torch 训练 ML 势：小分子/离子达化学精度，IL 离子对受数据规模限制（学习曲线证明需数百样本）。方法学：按组分归一化能量（507.7→0.3 meV）、RDKit 合理构型必需。工具链：PySCF+RDKit(WSL)+torch+mace-torch(Windows)。",
    "--highlights", "按组分归一化(1700倍)|IL数据规模限制|化学精度里程碑|PySCF-DFT-训练全链路|方法学报告",
    "--status", "进行中",
]
r2 = subprocess.run(cmd2, capture_output=True, text=True)
print("achievement:", r2.stdout.strip() or r2.stderr.strip())
