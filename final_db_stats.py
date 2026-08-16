# -*- coding: utf-8 -*-
"""final_db_stats.py — 数据库最终统计。"""
import sqlite3
import pathlib

db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("SELECT COUNT(*) FROM chem_literature")
print("chem_literature:", c.fetchone()[0])
c.execute("SELECT source, COUNT(*) FROM chem_literature GROUP BY source")
print("按源:", dict(c.fetchall()))
c.execute("SELECT COUNT(*) FROM interpretations")
print("interpretations:", c.fetchone()[0])
c.execute("SELECT COUNT(*) FROM interpretations WHERE title LIKE 'arXiv:%'")
print("arXiv 精读:", c.fetchone()[0])
db.close()

pdfs = list(pathlib.Path(r"D:\文献\chem-fulltext").glob("*.pdf"))
total = sum(p.stat().st_size for p in pdfs)
print(f"\n全文 PDF: {len(pdfs)} 篇 / {total/1024/1024:.0f} MB")

# IL DFT 数据
import json
il_files = ["dft_il_rdkit.jsonl", "dft_bmim_ntf2.jsonl", "dft_il_batch.jsonl"]
il_total = 0
for f in il_files:
    p = pathlib.Path(r"D:\Codex\MEC-Workspace\data") / f
    if p.exists():
        il_total += sum(1 for _ in p.open(encoding="utf-8"))
print(f"IL DFT 数据: {il_total} 样本")
