# -*- coding: utf-8 -*-
"""trend_analysis.py — 计算化学前沿趋势分析（基于 chem_literature）。

按年份统计各分类论文量 → 识别爆发方向 → 输出趋势报告。
"""
import sqlite3

db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()

print("=== 计算化学分类 × 年份 分布（2020-2026）===")
print(f"{'分类':<15} " + " ".join(f"{y}" for y in range(2020, 2027)))
c.execute("""SELECT category, year, COUNT(*) FROM chem_literature
             WHERE year >= 2020 AND year <= 2026
             GROUP BY category, year""")
data = c.fetchall()
by_cat = {}
for cat, yr, n in data:
    by_cat.setdefault(cat, {})[yr] = n

for cat in ["ml_potential", "dft", "wavefunction", "qmmm", "dynamics", "mechanism", "spectroscopy"]:
    row = by_cat.get(cat, {})
    counts = [str(row.get(y, 0)) for y in range(2020, 2027)]
    print(f"{cat:<15} " + " ".join(f"{v:>2}" for v in counts))

print("\n=== 2025-2026 增量（爆发检测）===")
c.execute("""SELECT category, COUNT(*) FROM chem_literature
             WHERE year >= 2025 GROUP BY category ORDER BY 2 DESC""")
for cat, n in c.fetchall():
    print(f"  {cat}: {n}")

print("\n=== 2025-2026 高价值新论文（按源）===")
c.execute("""SELECT source, COUNT(*) FROM chem_literature WHERE year >= 2025 GROUP BY source""")
for s, n in c.fetchall():
    print(f"  {s}: {n}")

db.close()
