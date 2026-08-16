# -*- coding: utf-8 -*-
"""check_tfn.py — 看 TFN 精读详情。"""
import sqlite3
db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("SELECT id, summary_cn, method, results, insights FROM interpretations WHERE title LIKE '%Tensor Field%' ORDER BY id DESC LIMIT 1")
r = c.fetchone()
if r:
    print("id:", r[0])
    print("摘要:", (r[1] or "")[:200])
    print("方法:", (r[2] or "")[:200])
    print("结果:", (r[3] or "")[:200])
    print("洞察:", (r[4] or "")[:300])
else:
    print("未找到 TFN 精读")
db.close()
