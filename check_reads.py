# -*- coding: utf-8 -*-
"""check_reads.py — 检查精读记录。"""
import sqlite3
db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("SELECT id, title, journal, year, status FROM interpretations WHERE relevance='计算化学前沿' OR doi LIKE '10.48550/%' ORDER BY id DESC LIMIT 10")
for r in c.fetchall():
    print(r)
db.close()
