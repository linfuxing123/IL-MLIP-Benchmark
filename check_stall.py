# -*- coding: utf-8 -*-
"""check_stall.py — 检查精读是否卡住。"""
import sqlite3
import time

db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("SELECT COUNT(*) FROM interpretations WHERE title LIKE 'arXiv:%'")
n1 = c.fetchone()[0]
print("当前 arXiv 精读:", n1)
c.execute("SELECT id, title FROM interpretations WHERE title LIKE 'arXiv:%' ORDER BY id DESC LIMIT 3")
for r in c.fetchall():
    print("最近:", r)
db.close()
time.sleep(30)

db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("SELECT COUNT(*) FROM interpretations WHERE title LIKE 'arXiv:%'")
n2 = c.fetchone()[0]
print("30 秒后:", n2)
print("增长:", n2 - n1, "→", "进行中" if n2 > n1 else "可能卡住")
db.close()
