#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""chem_ingest.py — 把 chem_*.jsonl 合并入库 mec.db。

建 chem_literature 表（id/title/authors/year/venue/abstract/doi/source/
category/citations/url/json/ingested_at），按 (source, id) 去重。
分类规则（计算化学博士级）：
  dft           — density functional / exchange-correlation
  wavefunction  — coupled cluster / MP2 / wavefunction / ab initio / CI
  ml_potential  — machine learning / neural network potential / force field
  qmmm          — QM/MM / hybrid
  dynamics      — molecular dynamics / simulation / trajectory
  mechanism     — reaction / transition state / catalysis
  spectroscopy  — spectroscopy / excited state / absorption
  gw_band       — GW / band gap / band structure
  other         — 兜底
"""
import json
import pathlib
import sqlite3
import re

DB = r"D:\Codex\MEC-Workspace\data\mec.db"
DATA = pathlib.Path(r"D:\Codex\MEC-Workspace\data")

CATEGORY_RULES = [
    ("dft", ["density functional", "exchange-correlation", "kohn-sham", "xc functional", "dft"]),
    ("wavefunction", ["coupled cluster", " mp2", "wavefunction", "ab initio", "configuration interaction", "ccsd", "full ci"]),
    ("ml_potential", ["machine learning potential", "neural network potential", "ml force field", "equivariant", "neural potential", "deep potential", "mace", "nep"]),
    ("qmmm", ["qm/mm", "qmmm", "hybrid qm"]),
    ("dynamics", ["molecular dynamics", "trajectory", "metadynamics", "replica exchange"]),
    ("mechanism", ["reaction mechanism", "transition state", "catalys", "cataly", "reaction path", "reaction coordinate"]),
    ("spectroscopy", ["spectroscop", "excited state", "absorption", "emission", "uv-vis", "ir spectrum"]),
    ("gw_band", ["gw approximation", "band gap", "band structure", "quasiparticle"]),
]

def categorize(text):
    t = (text or "").lower()
    for cat, kws in CATEGORY_RULES:
        for kw in kws:
            if kw in t:
                return cat
    return "other"

def main():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS chem_literature (
        id TEXT PRIMARY KEY,
        title TEXT,
        authors TEXT,
        year INTEGER,
        venue TEXT,
        abstract TEXT,
        doi TEXT,
        source TEXT,
        category TEXT,
        citations INTEGER,
        url TEXT,
        json TEXT,
        ingested_at TEXT DEFAULT (datetime('now'))
    )""")
    conn.commit()

    total_new = 0
    files = [
        ("chem_literature.jsonl", "arxiv"),
        ("chem_crossref.jsonl", "crossref"),
        ("chem_semantic.jsonl", "semanticscholar"),
        ("chem_github.jsonl", "github"),
    ]
    for fname, source in files:
        p = DATA / fname
        if not p.exists():
            print(f"跳过: {fname}（不存在）", flush=True)
            continue
        n_new = 0
        for line in p.open(encoding="utf-8"):
            try:
                r = json.loads(line)
            except Exception:
                continue
            # 统一 id
            if source == "arxiv":
                rid = r["id"]
                title, year = r["title"], int(r.get("published", "0")[:4] or 0)
                venue, abstract = "arXiv", r.get("summary", "")
                doi, cit, url = "", 0, r.get("id", "")
                authors = ", ".join(r.get("authors", []))
            elif source == "crossref":
                rid = f"doi:{r['DOI']}"
                title, year = r["title"], r.get("year") or 0
                venue, abstract = r.get("journal", ""), r.get("abstract", "")
                doi, cit, url = r["DOI"], 0, f"https://doi.org/{r['DOI']}"
                authors = ", ".join(r.get("authors", []))
            elif source == "semanticscholar":
                rid = r["paperId"]
                title, year = r.get("title"), r.get("year") or 0
                venue, abstract = r.get("venue", ""), r.get("abstract", "")
                doi = (r.get("externalIds") or {}).get("DOI", "")
                cit = r.get("citationCount") or 0
                url = f"https://doi.org/{doi}" if doi else f"https://api.semanticscholar.org/{r['paperId']}"
                authors = ", ".join(r.get("authors", []))
            else:  # github
                rid = f"github:{r['full_name']}"
                title = r.get("description") or r["full_name"]
                year = int((r.get("created_at") or "2020")[:4])
                venue = "GitHub"
                abstract = f"stars={r.get('stars')} lang={r.get('language')} topics={','.join(r.get('topics') or [])}"
                doi, cit, url = "", r.get("stars") or 0, r.get("url", "")
                authors = ""
            if not title:
                continue
            cat = categorize(f"{title} {abstract}")
            try:
                c.execute("INSERT OR IGNORE INTO chem_literature VALUES (?,?,?,?,?,?,?,?,?,?,?,?,datetime('now'))",
                          (rid, title[:500], authors[:1000], year, venue[:200], abstract[:4000],
                           doi, source, cat, cit, url, json.dumps(r, ensure_ascii=False)[:20000]))
                n_new += c.rowcount
            except Exception as ex:
                print(f"insert err: {ex}", flush=True)
        total_new += n_new
        print(f"{fname}: +{n_new}", flush=True)
    conn.commit()
    c.execute("SELECT COUNT(*) FROM chem_literature")
    print(f"chem_literature 总记录: {c.fetchone()[0]}", flush=True)
    c.execute("SELECT category, COUNT(*) FROM chem_literature GROUP BY category ORDER BY 2 DESC")
    for row in c.fetchall():
        print(f"  {row[0]}: {row[1]}", flush=True)
    conn.close()

if __name__ == "__main__":
    main()
