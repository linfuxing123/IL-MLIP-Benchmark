#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""crossref_fetch.py — 从 Crossref API 采集计算化学期刊论文（元数据级）。

覆盖期刊：JCTC（Journal of Chemical Theory and Computation）、JPC（Journal
of Physical Chemistry A/B/C）、J Chem Phys、J Comput Chem、J Chem Theory
Comput、WIREs Comput Mol Sci、Molecules 等。
查询：按期刊 ISSN + 主题词（DFT/ML potential/reaction 等）组合，取近期论文。
输出：data/chem_crossref.jsonl（增量去重）
"""
import json
import pathlib
import time
import urllib.parse
import urllib.request

OUT = pathlib.Path(r"D:\Codex\MEC-Workspace\data\chem_crossref.jsonl")
BASE = "https://api.crossref.org/works"

# 计算化学核心期刊 ISSN
JOURNALS = {
    "1549-9618": "JCTC",
    "1549-9626": "JPCL",     # J Phys Chem Lett
    "1089-5639": "JPCA",
    "1520-5215": "JPCB",
    "0021-9606": "JCP",
    "0192-8651": "JCC",
    "0887-6246": "J Polym Sci",
    "2470-1343": "ACS Omega",
}

TOPICS = [
    "density functional theory",
    "machine learning potential",
    "coupled cluster",
    "quantum chemistry",
    "molecular dynamics",
    "reaction mechanism",
    "excited state",
    "force field",
    "QM/MM",
]

def fetch(rows=20, cursor="*", query=None, issn=None):
    params = {
        "rows": rows,
        "cursor": cursor,
        "select": "DOI,title,author,container-title,issued,abstract,type,ISSN",
        "sort": "published",
        "order": "desc",
        "filter": "type:journal-article,from-pub-date:2024-01-01",
    }
    if query:
        params["query.title"] = query
    if issn:
        params["filter"] += f",issn:{issn}"
    url = f"{BASE}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"User-Agent": "MEC-chem-library/1.0 (mailto:3612411485@qq.com)"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    existing = set()
    if OUT.exists():
        for line in OUT.open(encoding="utf-8"):
            try:
                existing.add(json.loads(line).get("DOI"))
            except Exception:
                pass
    print(f"已有: {len(existing)}", flush=True)

    new_count = 0
    # 按主题检索（不限期刊，覆盖更广）
    for qi, topic in enumerate(TOPICS):
        try:
            data = fetch(query=topic, rows=15)
            items = data.get("message", {}).get("items", [])
            with OUT.open("a", encoding="utf-8") as f:
                for it in items:
                    doi = it.get("DOI")
                    if not doi or doi in existing:
                        continue
                    title = (it.get("title") or [""])[0]
                    if not title:
                        continue
                    rec = {
                        "DOI": doi,
                        "title": " ".join(title.split()),
                        "authors": [f"{a.get('given','')} {a.get('family','')}".strip() for a in (it.get("author") or [])[:8]],
                        "journal": (it.get("container-title") or [""])[0],
                        "year": (it.get("issued", {}).get("date-parts", [[None]])[0][0]),
                        "type": it.get("type"),
                        "topic_query": topic,
                        "source": "crossref",
                        "abstract": (it.get("abstract") or "")[:1000],
                    }
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    existing.add(doi)
                    new_count += 1
            print(f"[{qi+1}/{len(TOPICS)}] {topic[:40]} → {len(items)} 候选", flush=True)
        except Exception as ex:
            print(f"[{qi}] {topic} 失败: {str(ex)[:80]}", flush=True)
        time.sleep(0.5)

    # 按期刊 ISSN 补充（只取部分核心刊，避免过量）
    for isi, (issn, jname) in enumerate(JOURNALS.items()):
        try:
            data = fetch(issn=issn, rows=10)
            items = data.get("message", {}).get("items", [])
            with OUT.open("a", encoding="utf-8") as f:
                for it in items:
                    doi = it.get("DOI")
                    if not doi or doi in existing:
                        continue
                    title = (it.get("title") or [""])[0]
                    if not title:
                        continue
                    rec = {
                        "DOI": doi,
                        "title": " ".join(title.split()),
                        "authors": [f"{a.get('given','')} {a.get('family','')}".strip() for a in (it.get("author") or [])[:8]],
                        "journal": jname,
                        "year": (it.get("issued", {}).get("date-parts", [[None]])[0][0]),
                        "type": it.get("type"),
                        "topic_query": f"journal:{jname}",
                        "source": "crossref",
                    }
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    existing.add(doi)
                    new_count += 1
            print(f"[jrnl {isi+1}] {jname} → {len(items)} 候选", flush=True)
        except Exception as ex:
            print(f"[jrnl {isi+1}] {jname} 失败: {str(ex)[:80]}", flush=True)
        time.sleep(0.5)

    print(f"完成: 新增 {new_count}，累计 {len(existing)}", flush=True)

if __name__ == "__main__":
    main()
