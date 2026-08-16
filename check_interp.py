# -*- coding: utf-8 -*-
"""check_interp.py — 查 interpretations 表结构。"""
import sqlite3
db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("PRAGMA table_info(interpretations)")
for r in c.fetchall():
    print(r)
c.execute("SELECT COUNT(*) FROM interpretations")
print("行数:", c.fetchone()[0])
db.close()
