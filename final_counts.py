# -*- coding: utf-8 -*-
"""final_counts.py — 最终统计。"""
import sqlite3
db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("SELECT COUNT(*) FROM interpretations")
print("interpretations 总数:", c.fetchone()[0])
c.execute("SELECT COUNT(*) FROM interpretations WHERE title LIKE 'arXiv:%'")
print("arXiv 精读:", c.fetchone()[0])
c.execute("SELECT COUNT(*) FROM chem_literature")
print("chem_literature:", c.fetchone()[0])
db.close()
import pathlib
pdfs = list(pathlib.Path(r"D:\文献\chem-fulltext").glob("*.pdf"))
total = sum(p.stat().st_size for p in pdfs)
print(f"PDF: {len(pdfs)} 篇, {total/1024/1024:.0f} MB")
