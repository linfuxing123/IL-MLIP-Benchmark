# -*- coding: utf-8 -*-
"""goal_final_check.py — 目标最终验证：收集全部达成证据。"""
import pathlib
import sqlite3

db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()

print("=== ① 采集管线 ===")
c.execute("SELECT COUNT(*) FROM chem_literature")
print(f"  chem_literature: {c.fetchone()[0]} 条")
c.execute("SELECT source, COUNT(*) FROM chem_literature GROUP BY source")
print(f"  按源: {dict(c.fetchall())}")
c.execute("SELECT category, COUNT(*) FROM chem_literature GROUP BY category ORDER BY 2 DESC")
print(f"  按类: {dict(c.fetchall())}")

print("\n=== ④ DeepSeek 精读 ===")
c.execute("SELECT COUNT(*) FROM interpretations")
print(f"  interpretations: {c.fetchone()[0]} 条")
c.execute("SELECT COUNT(*) FROM interpretations WHERE title LIKE 'arXiv:%'")
print(f"  arXiv 全文精读: {c.fetchone()[0]}")

print("\n=== ③ 全文 PDF ===")
pdfs = list(pathlib.Path(r"D:\文献\chem-fulltext").glob("*.pdf"))
total = sum(p.stat().st_size for p in pdfs)
print(f"  PDF: {len(pdfs)} 篇 / {total/1024/1024:.0f} MB")

print("\n=== ⑤ 理论库 + 技能 ===")
theory = list(pathlib.Path(r"D:\Codex\.dsh\.agent-presets\math-agent-tools\skills\computational-chemistry\theory").glob("*.md"))
print(f"  理论库: {len(theory)} 篇")
skills = list(pathlib.Path(r"D:\Codex\.dsh\.agent-presets\math-agent-tools\skills").glob("*/SKILL.md"))
print(f"  预设技能: {[s.parent.name for s in skills]}")
db.close()
