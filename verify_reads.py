# -*- coding: utf-8 -*-
"""verify_reads.py — 验证批量精读真实入库量。"""
import sqlite3
db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("SELECT COUNT(*) FROM interpretations WHERE status='已解读'")
total = c.fetchone()[0]
print("已解读总数:", total)

# 本轮新增（relevance='计算化学前沿' 或 title 含 arXiv:）
c.execute("SELECT COUNT(*) FROM interpretations WHERE title LIKE 'arXiv:%'")
print("arXiv 标题精读:", c.fetchone()[0])

# 按 journal 分布
c.execute("SELECT journal, COUNT(*) FROM interpretations WHERE title LIKE 'arXiv:%' GROUP BY journal")
for r in c.fetchall():
    print(" ", r)
db.close()
