#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""semantic_fetch.py — Semantic Scholar API 采集计算化学论文（含引用数/影响力）。

Semantic Scholar Graph API：按主题检索，返回 citations/influentialCitationCount，
帮助识别"必读"高影响力论文。
输出：data/chem_semantic.jsonl（增量去重）
"""
import json
import pathlib
import time
import urllib.parse
import urllib.request

OUT = pathlib.Path(r"D:\Codex\MEC-Workspace\data\chem_semantic.jsonl")
BASE = "https://api.semanticscholar.org/graph/v1/paper/search"

QUERIES = [
    "machine learning interatomic potential",
    "density functional theory benchmark",
    "neural network potential molecular dynamics",
    "coupled cluster excited state",
    "QM/MM reaction mechanism",
    "equivariant neural network chemistry",
    "alphaFold protein structure" if False else "equivariant GNN force field",
    "GW approximation materials",
]

def fetch(query, limit=15):
    params = urllib.parse.urlencode({
        "query": query,
        "limit": limit,
        "fields": "title,abstract,authors,year,citationCount,influentialCitationCount,externalIds,venue,publicationTypes",
    })
    url = f"{BASE}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "MEC-chem-library/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    existing = set()
    if OUT.exists():
        for line in OUT.open(encoding="utf-8"):
            try:
                existing.add(json.loads(line).get("paperId"))
            except Exception:
                pass
    print(f"已有: {len(existing)}", flush=True)

    new_count = 0
    for qi, query in enumerate(QUERIES):
        try:
            data = fetch(query)
            papers = data.get("data", [])
            with OUT.open("a", encoding="utf-8") as f:
                for p in papers:
                    pid = p.get("paperId")
                    if not pid or pid in existing:
                        continue
                    rec = {
                        "paperId": pid,
                        "title": p.get("title"),
                        "abstract": (p.get("abstract") or "")[:1500],
                        "authors": [a.get("name", "") for a in (p.get("authors") or [])[:8]],
                        "year": p.get("year"),
                        "venue": p.get("venue"),
                        "citationCount": p.get("citationCount"),
                        "influentialCitationCount": p.get("influentialCitationCount"),
                        "externalIds": p.get("externalIds"),
                        "query": query,
                        "source": "semanticscholar",
                    }
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    existing.add(pid)
                    new_count += 1
            print(f"[{qi+1}/{len(QUERIES)}] {query[:40]} → {len(papers)} 候选", flush=True)
        except Exception as ex:
            print(f"[{qi}] {query} 失败: {str(ex)[:80]}", flush=True)
        time.sleep(2)  # S2 限速

    print(f"完成: 新增 {new_count}，累计 {len(existing)}", flush=True)

if __name__ == "__main__":
    main()
