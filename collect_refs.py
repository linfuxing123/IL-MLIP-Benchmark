# -*- coding: utf-8 -*-
"""collect_refs.py — 从精读库收集核心论文的 DOI（补 References）。"""
import sqlite3

db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()

# 核心论文（按标题关键词）
keywords = ["MACE", "Tensor Field", "Equivariant Graph", "SchNet", "Open Catalyst", "Machine Learning Force"]
for kw in keywords:
    c.execute("""SELECT title, doi, year FROM chem_literature
                 WHERE title LIKE ? AND doi != '' ORDER BY citations DESC LIMIT 3""", (f"%{kw}%",))
    print(f"\n【{kw}】")
    for r in c.fetchall():
        print(f"  {r[0][:60]} | doi={r[1]} | {r[2]}")
db.close()
