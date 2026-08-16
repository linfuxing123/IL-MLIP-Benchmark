# -*- coding: utf-8 -*-
"""check_mace.py — 看 MACE 精读记录详情。"""
import sqlite3
db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("SELECT id, title, method, results, insights FROM interpretations WHERE doi='10.48550/arXiv.2206.07697' ORDER BY id DESC LIMIT 1")
r = c.fetchone()
print("id:", r[0])
print("method:", (r[2] or "")[:300])
print("results:", (r[3] or "")[:300])
print("insights:", (r[4] or "")[:300])
db.close()
