# -*- coding: utf-8 -*-
"""survey_mlip.py — 从精读库生成 ML 势方法演进综述（博士级分析）。"""
import sqlite3

db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()

print("=" * 70)
print("ML 势方法演进（基于精读库 338 篇全文 + 594 篇文献）")
print("=" * 70)

# 1. 里程碑论文（高引）
print("\n【里程碑论文】")
c.execute("""SELECT title, year, citations FROM chem_literature
             WHERE source='semanticscholar' AND citations > 100
             ORDER BY citations DESC""")
for r in c.fetchall():
    print(f"  [{r[2]}引, {r[1]}] {r[0][:60]}")

# 2. 近期 ML 势方向（2024+）
print("\n【2024+ ML 势前沿（arXiv 精读）】")
c.execute("""SELECT title FROM interpretations
             WHERE title LIKE 'arXiv:%' AND summary_cn LIKE '%potential%'
             AND (summary_cn LIKE '%force field%' OR summary_cn LIKE '%equivariant%')
             LIMIT 12""")
for r in c.fetchall():
    print(f"  • {r[0]}")

# 3. 分类统计
print("\n【文献分类分布】")
c.execute("SELECT category, COUNT(*) FROM chem_literature GROUP BY category ORDER BY 2 DESC")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")

# 4. 高价值开源工具（GitHub）
print("\n【高星开源工具】")
c.execute("SELECT title, url, citations FROM chem_literature WHERE source='github' ORDER BY citations DESC LIMIT 8")
for r in c.fetchall():
    print(f"  [{r[2]}★] {r[0][:50]}")
db.close()
