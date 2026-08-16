# -*- coding: utf-8 -*-
"""check_tfn2.py — 查 TFN 精读（按 arXiv id）。"""
import sqlite3
db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("SELECT id, title, summary_cn FROM interpretations WHERE title LIKE '%1802.08219%' ORDER BY id DESC LIMIT 1")
r = c.fetchone()
if r:
    print("id:", r[0])
    print("title:", r[1])
    print("摘要:", (r[2] or "")[:300])
else:
    print("未找到")
db.close()
