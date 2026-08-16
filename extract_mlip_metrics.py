# -*- coding: utf-8 -*-
"""extract_mlip_metrics.py — 从精读库提取 ML 势论文的关键性能指标。

目标：从 591 篇 arXiv 精读的 insights（含关键数值）中，提取常见性能指标
（MAE meV/atom、力 MAE、数据集名），生成对比表——验证知识库的深度价值。
"""
import re
import sqlite3

db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()

# 1. 找含能量/力 MAE 的精读记录
c.execute("""SELECT title, insights FROM interpretations
             WHERE title LIKE 'arXiv:%' AND insights LIKE '%meV%'""")
rows = c.fetchall()
print(f"含 meV 指标的精读: {len(rows)} 篇\n")

# 2. 提取数值模式
metric_pat = re.compile(r"(\d+\.?\d*)\s*(meV/atom|meV/Å|meV|kcal/mol|meV per atom)", re.I)
print("=== ML 势性能指标样本 ===")
count = 0
for title, insights in rows:
    found = metric_pat.findall(insights or "")
    if found and count < 15:
        print(f"▶ {title}")
        print(f"  {found[:6]}")
        count += 1

# 3. 数据集提及频率
print("\n=== 常用数据集提及（精读库）===")
datasets = ["ANI-1", "QM9", "MD17", "OC20", "MD22", "rMD17", "QM7"]
for ds in datasets:
    c.execute("SELECT COUNT(*) FROM interpretations WHERE insights LIKE ? OR summary_cn LIKE ?",
              (f"%{ds}%", f"%{ds}%"))
    print(f"  {ds}: {c.fetchone()[0]} 篇")

db.close()
