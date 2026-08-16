#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""incremental_update.py — 计算化学文献增量更新（可每日调度）。

流程：
1. arXiv：按主题拉最近 7 天新论文（增量，去重）
2. Crossref：按主题拉最近 7 天新论文
3. 新论文自动抓全文 PDF（arXiv）
4. 新全文自动精读入库
5. 输出新增统计

用法：python incremental_update.py [--days 7] [--fetch-pdf] [--interpret]
"""
import argparse
import json
import pathlib
import re
import sqlite3
import subprocess
import sys
import time
import urllib.parse
import urllib.request

WORKSPACE = pathlib.Path(r"D:\Codex\MEC-Workspace")
CHEM_LIB = WORKSPACE / "workspace" / "chem-library"
DATA = WORKSPACE / "data"
FULLTEXT = pathlib.Path(r"D:\文献\chem-fulltext")
PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"

ARXIV_TOPICS = [
    'cat:physics.chem-ph AND (all:"coupled cluster" OR all:"MP2" OR all:"quantum chemistry")',
    'cat:physics.chem-ph AND all:"density functional theory"',
    'cat:physics.chem-ph AND (all:"machine learning potential" OR all:"neural network potential")',
    'cat:physics.chem-ph AND all:"molecular dynamics"',
]

def fetch_arxiv(query, days=7, max_results=30):
    """拉最近 days 天 arXiv 新论文。"""
    url = ("http://export.arxiv.org/api/query?" + urllib.parse.urlencode({
        "search_query": query, "start": 0, "max_results": max_results,
        "sortBy": "submittedDate", "sortOrder": "descending"}))
    req = urllib.request.Request(url, headers={"User-Agent": "MEC-chem-library/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")

def parse_entries(xml):
    entries = []
    for block in xml.split("<entry>"):
        if not block.strip():
            continue
        def grab(tag):
            s = block.find(f"<{tag}>")
            if s < 0:
                return None
            e = block.find(f"</{tag}>", s)
            return block[s + len(tag) + 2:e] if e > 0 else None
        eid = grab("id")
        title = grab("title")
        if eid and title and not title.strip().startswith("arXiv Query"):
            e = {"id": eid, "title": " ".join(title.split()),
                 "summary": grab("summary"), "published": grab("published"),
                 "source": "arxiv"}
            authors = []
            idx = 0
            while True:
                a = block.find("<name>", idx)
                if a < 0:
                    break
                ae = block.find("</name>", a)
                authors.append(block[a + 6:ae].strip())
                idx = ae + 7
            e["authors"] = authors
            entries.append(e)
    return entries

def fetch_crossref(days=7):
    """Crossref 最近 7 天计算化学论文。"""
    import datetime
    cutoff = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    params = {
        "rows": 30, "sort": "published", "order": "desc",
        "select": "DOI,title,author,container-title,issued",
        "filter": f"type:journal-article,from-pub-date:{cutoff}",
        "query.title": "density functional theory OR machine learning potential OR coupled cluster",
    }
    url = "https://api.crossref.org/works?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "MEC-chem-library/1.0 (mailto:3612411485@qq.com)"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--fetch-pdf", action="store_true", help="抓新论文全文 PDF")
    ap.add_argument("--interpret", action="store_true", help="新 PDF 精读")
    args = ap.parse_args()

    # 已存在 id
    conn = sqlite3.connect(DATA / "mec.db")
    c = conn.cursor()
    c.execute("SELECT DISTINCT id FROM chem_literature")
    existing = {r[0] for r in c.fetchall()}
    print(f"库中已有: {len(existing)} 条", flush=True)

    # 1. arXiv 增量
    new_arxiv = 0
    for qi, query in enumerate(ARXIV_TOPICS):
        try:
            xml = fetch_arxiv(query, args.days)
            for e in parse_entries(xml):
                if e["id"] in existing:
                    continue
                year = int((e.get("published") or "0")[:4] or 0)
                c.execute("""INSERT OR IGNORE INTO chem_literature
                    (id, title, authors, year, venue, abstract, doi, source, category, citations, url, json)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (e["id"], e["title"][:500], ", ".join(e.get("authors", []))[:1000],
                     year, "arXiv", (e.get("summary") or "")[:4000],
                     "", "arxiv", "other", 0, e["id"],
                     json.dumps(e, ensure_ascii=False)[:20000]))
                if c.rowcount:
                    existing.add(e["id"])
                    new_arxiv += 1
        except Exception as ex:
            print(f"[arxiv {qi}] {str(ex)[:60]}", flush=True)
        time.sleep(0.5)
    conn.commit()
    print(f"arXiv 新增: {new_arxiv}", flush=True)

    # 2. Crossref 增量
    new_crossref = 0
    try:
        data = fetch_crossref(args.days)
        for it in data.get("message", {}).get("items", []):
            doi = it.get("DOI")
            if not doi or f"doi:{doi}" in existing:
                continue
            title = (it.get("title") or [""])[0]
            if not title:
                continue
            rid = f"doi:{doi}"
            rec = {"DOI": doi, "title": title,
                   "authors": [f"{a.get('given','')} {a.get('family','')}".strip() for a in (it.get("author") or [])[:8]],
                   "journal": (it.get("container-title") or [""])[0],
                   "year": (it.get("issued", {}).get("date-parts", [[None]])[0][0]),
                   "source": "crossref"}
            c.execute("""INSERT OR IGNORE INTO chem_literature
                (id, title, authors, year, venue, abstract, doi, source, category, citations, url, json)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                (rid, title[:500], ", ".join(rec["authors"])[:1000],
                 rec["year"] or 0, rec["journal"][:200], "", doi, "crossref",
                 "other", 0, f"https://doi.org/{doi}",
                 json.dumps(rec, ensure_ascii=False)[:20000]))
            if c.rowcount:
                existing.add(rid)
                new_crossref += 1
    except Exception as ex:
        print(f"[crossref] {str(ex)[:80]}", flush=True)
    conn.commit()
    print(f"Crossref 新增: {new_crossref}", flush=True)

    # 3. 抓新 arXiv 全文
    if args.fetch_pdf:
        c.execute("SELECT id, title FROM chem_literature WHERE source='arxiv'")
        got_pdf = 0
        for pid, title in c.fetchall():
            m = re.search(r"arxiv\.org/abs/([\w.]+)", pid or "")
            if not m:
                continue
            arxiv_id = m.group(1)
            safe = arxiv_id.replace("/", "_")
            pdf_path = FULLTEXT / f"arxiv_{safe}.pdf"
            if pdf_path.exists():
                continue
            try:
                req = urllib.request.Request(f"https://arxiv.org/pdf/{arxiv_id}",
                                             headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=60) as resp:
                    data = resp.read()
                if data[:4] == b"%PDF":
                    pdf_path.write_bytes(data)
                    got_pdf += 1
                    print(f"  PDF: {arxiv_id}", flush=True)
            except Exception:
                pass
            time.sleep(0.3)
        print(f"新抓 PDF: {got_pdf}", flush=True)

    # 4. 精读新 PDF
    if args.interpret:
        r = subprocess.run([PY, str(CHEM_LIB / "interpret_all.py")],
                           capture_output=True, text=True, timeout=3600)
        print(f"精读: {r.stdout[-200:] if r.stdout else 'done'}", flush=True)

    c.execute("SELECT COUNT(*) FROM chem_literature")
    print(f"库总量: {c.fetchone()[0]}", flush=True)
    conn.close()

if __name__ == "__main__":
    main()
