#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""arxiv_broad.py — arXiv 广谱抓取（20 主题覆盖计算化学全方向）。

相比之前的 10 主题，扩展到 20 主题（加催化、材料、电池、光谱、溶剂化、
量子动力学等），最大化开放全文覆盖。
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

TOPICS = [
    'cat:physics.chem-ph AND all:"machine learning potential"',
    'cat:physics.chem-ph AND all:"density functional theory"',
    'cat:physics.chem-ph AND all:"coupled cluster"',
    'cat:physics.chem-ph AND all:"molecular dynamics"',
    'cat:physics.chem-ph AND all:"QM/MM"',
    'cat:physics.chem-ph AND all:"ionic liquid"',
    'cat:physics.chem-ph AND all:"electrolyte"',
    'cat:physics.chem-ph AND all:"lithium battery"',
    'cat:physics.chem-ph AND all:"catalysis"',
    'cat:physics.chem-ph AND all:"solvation"',
    'cat:physics.chem-ph AND all:"spectroscopy"',
    'cat:physics.chem-ph AND all:"excited state"',
    'cat:physics.chem-ph AND all:"force field"',
    'cat:physics.chem-ph AND all:"transition state"',
    'cat:physics.chem-ph AND all:"quantum dynamics"',
    'cat:physics.chem-ph AND all:"materials discovery"',
    'cat:cond-mat.mtrl-sci AND all:"electrolyte"',
    'cat:cond-mat.mtrl-sci AND all:"solid electrolyte"',
    'cat:physics.chem-ph AND all:"free energy"',
    'cat:physics.chem-ph AND all:"polarizable"',
]

def fetch(query, max_results=30):
    url = ("http://export.arxiv.org/api/query?" + urllib.parse.urlencode({
        "search_query": query, "start": 0, "max_results": max_results,
        "sortBy": "submittedDate", "sortOrder": "descending"}))
    req = urllib.request.Request(url, headers={"User-Agent": "MEC-chem/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")

def parse(xml):
    out = []
    for blk in xml.split("<entry>"):
        if not blk.strip():
            continue
        def g(tag):
            s = blk.find(f"<{tag}>")
            if s < 0: return None
            e = blk.find(f"</{tag}>", s)
            return blk[s+len(tag)+2:e] if e > 0 else None
        i = g("id"); t = g("title")
        if i and t and not t.strip().startswith("arXiv Query"):
            out.append({"id": i, "title": " ".join(t.split()),
                        "published": g("published")})
    return out

def main():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT DISTINCT id FROM chem_literature WHERE source='arxiv'")
    existing = {r[0] for r in c.fetchall()}

    new_meta, new_pdf = 0, 0
    for qi, q in enumerate(TOPICS):
        try:
            xml = fetch(q)
            for e in parse(xml):
                if e["id"] in existing:
                    continue
                year = int((e.get("published") or "0")[:4] or 0)
                c.execute("""INSERT OR IGNORE INTO chem_literature
                    (id,title,authors,year,venue,abstract,doi,source,category,citations,url,json)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (e["id"], e["title"][:500], "", year, "arXiv", "",
                     "", "arxiv", "other", 0, e["id"],
                     json.dumps(e, ensure_ascii=False)[:5000]))
                if c.rowcount:
                    existing.add(e["id"]); new_meta += 1
                # 抓 PDF
                m = re.search(r"arxiv\.org/abs/([\w.]+)", e["id"])
                if m:
                    aid = m.group(1).replace("/", "_")
                    pdf = OUT_DIR / f"arxiv_{aid}.pdf"
                    if not pdf.exists():
                        try:
                            req = urllib.request.Request(f"https://arxiv.org/pdf/{m.group(1)}",
                                                         headers={"User-Agent": "Mozilla/5.0"})
                            with urllib.request.urlopen(req, timeout=60) as resp:
                                d = resp.read()
                            if d[:4] == b"%PDF":
                                pdf.write_bytes(d); new_pdf += 1
                        except Exception:
                            pass
                        time.sleep(0.3)
        except Exception as ex:
            print(f"[{qi}] {q[:40]} 失败 {str(ex)[:40]}", flush=True)
        time.sleep(0.5)
    conn.commit()
    c.execute("SELECT COUNT(*) FROM chem_literature WHERE source='arxiv'")
    print(f"arXiv 库: {c.fetchone()[0]} 条 | 新增元数据 {new_meta} | 新 PDF {new_pdf}", flush=True)
    conn.close()

if __name__ == "__main__":
    main()
