# -*- coding: utf-8 -*-
"""quality_stats.py — 精读质量统计。"""
import sqlite3
db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("SELECT COUNT(*) FROM interpretations WHERE title LIKE 'arXiv:%' AND summary_cn IS NOT NULL AND summary_cn != ''")
print("arXiv 精读含摘要:", c.fetchone()[0])
c.execute("SELECT COUNT(*) FROM interpretations WHERE title LIKE 'arXiv:%' AND insights LIKE '%关键数值%'")
print("arXiv 精读含数值:", c.fetchone()[0])
c.execute("SELECT COUNT(*) FROM interpretations WHERE title LIKE 'arXiv:%' AND (method IS NOT NULL AND method != '')")
print("arXiv 精读含方法节:", c.fetchone()[0])
c.execute("SELECT COUNT(*) FROM interpretations WHERE title LIKE 'arXiv:%' AND (results IS NOT NULL AND results != '')")
print("arXiv 精读含结果节:", c.fetchone()[0])
db.close()
