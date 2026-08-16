#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch_arxiv_all.py — 抓取所有 arXiv 源论文全文（source='arxiv' 的全部 + DOI 含 arXiv 的）。"""
import pathlib
import re
import sqlite3
import time
import urllib.request

DB = r"D:\Codex\MEC-Workspace\data\mec.db"
OUT_DIR = pathlib.Path(r"D:\文献\chem-fulltext")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    db = sqlite3.connect(DB)
    c = db.cursor()
    # 全部 arxiv 源 + 高引优先
    c.execute("""SELECT id, title, citations FROM chem_literature
                 WHERE source='arxiv' ORDER BY citations DESC""")
    papers = c.fetchall()
    print(f"arXiv 源论文: {len(papers)} 篇", flush=True)

    ok = fail = skip = 0
    for pid, title, cit in papers:
        # 从 id 提取 arXiv 编号：http://arxiv.org/abs/XXXX
        m = re.search(r"arxiv\.org/abs/([\w.]+)", pid)
        if not m:
            skip += 1
            continue
        arxiv_id = m.group(1)
        safe = arxiv_id.replace("/", "_")
        pdf_path = OUT_DIR / f"arxiv_{safe}.pdf"
        if pdf_path.exists():
            skip += 1
            continue
        url = f"https://arxiv.org/pdf/{arxiv_id}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            if data[:4] == b"%PDF":
                pdf_path.write_bytes(data)
                ok += 1
                print(f"✓ {arxiv_id} [{cit}引] {title[:45]} ({len(data)//1024}KB)", flush=True)
            else:
                fail += 1
                print(f"✗ {arxiv_id} 非 PDF", flush=True)
        except Exception as ex:
            fail += 1
            print(f"✗ {arxiv_id} {str(ex)[:50]}", flush=True)
        time.sleep(0.5)

    print(f"完成: {ok} 成功 / {fail} 失败 / {skip} 跳过", flush=True)
    db.close()

if __name__ == "__main__":
    main()
