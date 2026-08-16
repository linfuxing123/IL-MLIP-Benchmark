# -*- coding: utf-8 -*-
"""todo_pdfs.py — 计算待精读 PDF。"""
import pathlib
import re
import sqlite3

pdfs = [p for p in pathlib.Path(r"D:\文献\chem-fulltext").glob("*.pdf")]
db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("SELECT DISTINCT title FROM interpretations WHERE title LIKE 'arXiv:%'")
done = {str(r[0]) for r in c.fetchall()}

def norm(s):
    s = s.replace("arXiv:", "").replace("arxiv_", "")
    s = re.sub(r"v\d+$", "", s).lower()
    return s

done_norm = {norm(t) for t in done}
todo = []
for p in pdfs:
    pid = norm(p.stem)
    if pid not in done_norm:
        todo.append(p.name)
print(f"PDF 总数: {len(pdfs)}")
print(f"已精读 arXiv 记录: {len(done)}")
print(f"待精读 PDF: {len(todo)}")
for t in todo[:20]:
    print("  ", t)
db.close()
