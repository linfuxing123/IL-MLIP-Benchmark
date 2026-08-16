#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch_arxiv_fulltext.py — 抓取高价值论文的 arXiv 开放全文 PDF。

从 chem_literature 表选出 DOI 为 arXiv 的论文，下载 PDF 到 D:\文献\chem-fulltext\。
arXiv PDF 下载：https://arxiv.org/pdf/<id>（id 从 DOI 10.48550/arXiv.xxx 提取）。
"""
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
    # 选 arXiv DOI + 高引（或全部 arXiv 有引用的）
    c.execute("""SELECT doi, title, citations FROM chem_literature
                 WHERE doi LIKE '10.48550/%' AND citations > 0
                 ORDER BY citations DESC""")
    papers = c.fetchall()
    print(f"arXiv 高引论文: {len(papers)} 篇", flush=True)

    ok = fail = 0
    for doi, title, cit in papers:
        # 从 DOI 提取 arXiv id
        m = re.search(r"10\.48550/arXiv\.([\w.]+)", doi)
        if not m:
            continue
        arxiv_id = m.group(1)
        # 处理旧格式 arXiv:1234.5678v1
        safe = arxiv_id.replace("/", "_")
        pdf_path = OUT_DIR / f"arxiv_{safe}.pdf"
        if pdf_path.exists():
            print(f"跳过（已有）: {arxiv_id}", flush=True)
            continue
        url = f"https://arxiv.org/pdf/{arxiv_id}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            pdf_path.write_bytes(data)
            # 验证 PDF 魔数
            if data[:4] == b"%PDF":
                ok += 1
                print(f"✓ {arxiv_id} [{cit}引] {title[:40]} ({len(data)//1024}KB)", flush=True)
            else:
                pdf_path.unlink(missing_ok=True)
                print(f"✗ {arxiv_id} 非 PDF", flush=True)
                fail += 1
        except Exception as ex:
            print(f"✗ {arxiv_id} {str(ex)[:60]}", flush=True)
            fail += 1
        time.sleep(1)

    print(f"完成: {ok} 成功 / {fail} 失败", flush=True)
    db.close()

if __name__ == "__main__":
    main()
