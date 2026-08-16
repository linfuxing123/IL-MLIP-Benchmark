# -*- coding: utf-8 -*-
"""check_chem_db.py — 检查 chem_literature 质量。"""
import sqlite3

db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("SELECT source, COUNT(*) FROM chem_literature GROUP BY source")
print("按源:", dict(c.fetchall()))

c.execute("""SELECT title, year, venue, citations FROM chem_literature
             WHERE source='semanticscholar' ORDER BY citations DESC LIMIT 5""")
print("\nSemantic Scholar 高引论文:")
for r in c.fetchall():
    print(f"  [{r[3]} 引] {r[0][:60]} ({r[1]})")

c.execute("""SELECT title, url, citations FROM chem_literature
             WHERE source='github' ORDER BY citations DESC LIMIT 5""")
print("\nGitHub 高星仓库:")
for r in c.fetchall():
    print(f"  [{r[2]}★] {r[0][:60]}")

c.execute("SELECT COUNT(DISTINCT id) FROM chem_literature")
print("\n唯一 id:", c.fetchone()[0])

c.execute("SELECT COUNT(*) FROM chem_literature WHERE year >= 2024")
print("2024+ 论文:", c.fetchone()[0])

c.execute("SELECT COUNT(*) FROM chem_literature WHERE abstract != '' AND abstract IS NOT NULL")
print("有摘要:", c.fetchone()[0])
db.close()
