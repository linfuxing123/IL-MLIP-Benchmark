#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""interpret_all.py — 批量精读 chem-fulltext 目录所有 PDF（跳过已解读的）。"""
import pathlib
import re
import sqlite3
import subprocess
import sys

FULLTEXT = pathlib.Path(r"D:\文献\chem-fulltext")
DB = r"D:\Codex\MEC-Workspace\data\mec.db"
SCRIPT = pathlib.Path(__file__).resolve().parent / "interpret_pdf.py"
PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"

def main():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT DISTINCT title FROM interpretations WHERE title IS NOT NULL")
    done_titles = {r[0] for r in c.fetchall()}
    conn.close()

    pdfs = sorted(FULLTEXT.glob("*.pdf"))
    print(f"待处理 PDF: {len(pdfs)}", flush=True)

    ok = 0
    for pdf in pdfs:
        # 从文件名推断 arXiv id / DOI
        name = pdf.stem  # arxiv_2206.07697 或 acs_10_1021_...
        title_guess = name.replace("arxiv_", "arXiv:").replace("_", ".")
        cmd = [PY, str(SCRIPT), str(pdf), "--title", title_guess,
               "--journal", "arXiv" if name.startswith("arxiv") else "期刊",
               "--relevance", "计算化学前沿"]
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=300,
                               encoding="utf-8", errors="replace")
            if "已入库" in (r.stdout or ""):
                ok += 1
                print(f"✓ {name}", flush=True)
            else:
                print(f"? {name}: {(r.stdout or '')[:40]} {(r.stderr or '')[:40]}", flush=True)
        except Exception as ex:
            print(f"✗ {name}: {str(ex)[:60]}", flush=True)
    print(f"完成: {ok} 篇精读", flush=True)

if __name__ == "__main__":
    main()
