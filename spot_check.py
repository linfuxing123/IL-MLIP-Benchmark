# -*- coding: utf-8 -*-
"""spot_check.py — 抽查精读质量。"""
import sqlite3
db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("""SELECT title, length(summary_cn), length(method), length(results), length(insights)
             FROM interpretations WHERE title LIKE 'arXiv:%' AND summary_cn != ''
             ORDER BY id DESC LIMIT 5""")
print("最近 5 篇精读（标题/摘要/方法/结果/洞察 长度）:")
for r in c.fetchall():
    print(f"  {r[0][:40]} | 摘要{r[1]} 方法{r[2]} 结果{r[3]} 洞察{r[4]}")
db.close()
