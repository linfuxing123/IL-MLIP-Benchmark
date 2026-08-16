# -*- coding: utf-8 -*-
"""demo_query.py — 演示：从精读库查 ML 势方向代表方法。"""
import sqlite3
db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()

print("=== ML 势方向精读论文（含摘要）===")
c.execute("""SELECT title, summary_cn FROM interpretations
             WHERE title LIKE 'arXiv:%'
             AND (summary_cn LIKE '%neural network potential%' OR summary_cn LIKE '%equivariant%' OR summary_cn LIKE '%machine learning%force%')
             LIMIT 8""")
for r in c.fetchall():
    print(f"\n▶ {r[0]}")
    print(f"  {r[1][:120]}...")

print("\n=== chem_literature 按分类统计 ===")
c.execute("SELECT category, COUNT(*) FROM chem_literature GROUP BY category ORDER BY 2 DESC")
for r in c.fetchall():
    print(f"  {r[0]}: {r[1]}")
db.close()
