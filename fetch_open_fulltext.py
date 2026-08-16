#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fetch_open_fulltext.py — 多源开放全文抓取（绕过 Cloudflare）。

源（全部开放、无 Cloudflare 拦截）：
1. PMC（PubMed Central）：NLM E-utilities API，OA 全文
2. ChemRxiv：预印本 API
3. arXiv（已有，续增量）
4. Semantic Scholar openAccessPdf 字段

策略：从 chem_literature 库找 DOI，逐个源尝试拿开放全文。
输出：D:\文献\chem-fulltext\ + 更新数据库。
"""
import json
import pathlib
import re
import sqlite3
import time
import urllib.parse
import urllib.request

DB = r"D:\Codex\MEC-Workspace\data\mec.db"
OUT_DIR = pathlib.Path(r"D:\文献\chem-fulltext")
OUT_DIR.mkdir(parents=True, exist_ok=True)
UA = "MEC-chem-library/1.0 (mailto:3612411485@qq.com)"

def fetch(url, timeout=60, headers=None):
    h = {"User-Agent": UA}
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()

def pmc_fulltext(doi):
    """PMC ID 查询 + 全文下载。"""
    # 用 ID Converter 找 PMC ID
    base = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
    params = urllib.parse.urlencode({"ids": doi, "format": "json", "tool": "mec", "email": "3612411485@qq.com"})
    data = json.loads(fetch(base + "?" + params))
    for rec in data.get("records", []):
        if rec.get("pmcid"):
            pmcid = rec["pmcid"]
            # PMC OA 全文
            for ext in ["pdf", "pdf/"]:
                try:
                    url = f"https://www.ncbi.nlm.nih.gov/pmc/articles/{pmcid}/pdf/"
                    return fetch(url, timeout=120)
                except Exception:
                    continue
    return None

def chemrxiv_fulltext(doi):
    """ChemRxiv 全文。"""
    try:
        url = f"https://chemrxiv.org/engage/chemrxiv/search-dashboard?text={urllib.parse.quote(doi)}"
        data = fetch(url, timeout=60)
        return data if b"%PDF" in data[:20] else None
    except Exception:
        return None

def main():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    # 选有 DOI 的高价值论文
    c.execute("""SELECT doi, title FROM chem_literature
                 WHERE doi != '' AND doi NOT LIKE '10.48550/%'
                 ORDER BY citations DESC LIMIT 30""")
    papers = c.fetchall()
    print(f"尝试抓取 {len(papers)} 篇有 DOI 论文的开放全文", flush=True)

    ok = 0
    for doi, title in papers:
        safe = doi.replace("/", "_").replace(".", "_")
        pdf_path = OUT_DIR / f"open_{safe}.pdf"
        if pdf_path.exists():
            continue
        # 1. PMC
        try:
            data = pmc_fulltext(doi)
            if data and data[:4] == b"%PDF":
                pdf_path.write_bytes(data)
                print(f"✓ PMC: {doi} ({len(data)//1024}KB)", flush=True)
                ok += 1
                time.sleep(1)
                continue
        except Exception:
            pass
        time.sleep(1)
    print(f"完成: {ok} 篇开放全文", flush=True)
    conn.close()

if __name__ == "__main__":
    main()
