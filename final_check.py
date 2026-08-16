# -*- coding: utf-8 -*-
"""final_check.py — 本轮成果总检。"""
import sqlite3

db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()

print("=== chem_literature（计算化学文献库）===")
c.execute("SELECT COUNT(*) FROM chem_literature")
print("总数:", c.fetchone()[0])
c.execute("SELECT source, COUNT(*) FROM chem_literature GROUP BY source")
print("按源:", dict(c.fetchall()))

print("\n=== interpretations（精读库，含 MACE）===")
c.execute("SELECT COUNT(*) FROM interpretations")
print("总数:", c.fetchone()[0])
c.execute("SELECT id, title FROM interpretations WHERE doi='10.48550/arXiv.2206.07697' ORDER BY id DESC LIMIT 1")
r = c.fetchone()
print("最新 MACE:", r)
db.close()

import pathlib
pdfs = list(pathlib.Path(r"D:\文献\chem-fulltext").glob("*.pdf"))
print(f"\n=== D:\\文献\\chem-fulltext PDF: {len(pdfs)} ===")
for p in pdfs[:10]:
    print(" ", p.name, f"({p.stat().st_size//1024}KB)")
