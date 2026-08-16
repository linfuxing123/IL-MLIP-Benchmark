#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch_semantic_arxiv.py — 抓 Semantic 记录中带 ArXiv ID 的论文全文 + 回填 DOI。"""
import json
import pathlib
import re
import sqlite3
import time
import urllib.request

SEMANTIC = r"D:\Codex\MEC-Workspace\data\chem_semantic.jsonl"
DB = r"D:\Codex\MEC-Workspace\data\mec.db"
OUT_DIR = pathlib.Path(r"D:\文献\chem-fulltext")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    # 1. 抓 PDF
    ok = fail = 0
    for line in open(SEMANTIC, encoding="utf-8"):
        r = json.loads(line)
        ext = r.get("externalIds") or {}
        arxiv = ext.get("ArXiv")
        if not arxiv:
            continue
        safe = arxiv.replace("/", "_")
        pdf_path = OUT_DIR / f"arxiv_{safe}.pdf"
        if pdf_path.exists():
            continue
        url = f"https://arxiv.org/pdf/{arxiv}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            if data[:4] == b"%PDF":
                pdf_path.write_bytes(data)
                ok += 1
                print(f"✓ {arxiv} | {r['title'][:45]}", flush=True)
            else:
                fail += 1
        except Exception as ex:
            fail += 1
            print(f"✗ {arxiv} {str(ex)[:40]}", flush=True)
        time.sleep(0.5)

    # 2. 回填 DOI 到 chem_literature（semantic 的 DOI）
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    for line in open(SEMANTIC, encoding="utf-8"):
        r = json.loads(line)
        ext = r.get("externalIds") or {}
        doi = ext.get("DOI")
        if doi:
            c.execute("UPDATE chem_literature SET doi=? WHERE id=?", (doi, f"semantic:{r['paperId']}"))
    conn.commit()
    c.execute("SELECT COUNT(*) FROM chem_literature WHERE doi != ''")
    print(f"回填后含 DOI 论文: {c.fetchone()[0]}", flush=True)
    conn.close()
    print(f"PDF: {ok} 成功 / {fail} 失败", flush=True)

if __name__ == "__main__":
    main()
