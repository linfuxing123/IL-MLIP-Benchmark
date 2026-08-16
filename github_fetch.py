#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""github_fetch.py — GitHub API 采集计算化学开源方法/代码仓库。

搜索计算化学核心开源项目（star 排序），入库供方法学习。
输出：data/chem_github.jsonl（增量去重）
"""
import json
import pathlib
import time
import urllib.parse
import urllib.request

OUT = pathlib.Path(r"D:\Codex\MEC-Workspace\data\chem_github.jsonl")
BASE = "https://api.github.com/search/repositories"

QUERIES = [
    "machine learning potential",
    "neural network potential chemistry",
    "quantum chemistry DFT",
    "QM/MM simulation",
    "molecular dynamics force field",
    "equivariant neural network",
    "electronic structure calculation",
    "reaction path search",
]

def fetch(query, per_page=10):
    params = urllib.parse.urlencode({
        "q": f"{query} stars:>20",
        "sort": "stars",
        "order": "desc",
        "per_page": per_page,
    })
    url = f"{BASE}?{params}"
    req = urllib.request.Request(url, headers={
        "User-Agent": "MEC-chem-library/1.0",
        "Accept": "application/vnd.github+json",
    })
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    existing = set()
    if OUT.exists():
        for line in OUT.open(encoding="utf-8"):
            try:
                existing.add(json.loads(line).get("full_name"))
            except Exception:
                pass
    print(f"已有: {len(existing)}", flush=True)

    new_count = 0
    for qi, query in enumerate(QUERIES):
        try:
            data = fetch(query)
            repos = data.get("items", [])
            with OUT.open("a", encoding="utf-8") as f:
                for r in repos:
                    name = r.get("full_name")
                    if not name or name in existing:
                        continue
                    rec = {
                        "full_name": name,
                        "description": r.get("description"),
                        "url": r.get("html_url"),
                        "stars": r.get("stargazers_count"),
                        "language": r.get("language"),
                        "topics": r.get("topics"),
                        "created_at": r.get("created_at"),
                        "updated_at": r.get("updated_at"),
                        "query": query,
                        "source": "github",
                    }
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
                    existing.add(name)
                    new_count += 1
            print(f"[{qi+1}/{len(QUERIES)}] {query[:40]} → {len(repos)} 候选", flush=True)
        except Exception as ex:
            print(f"[{qi}] {query} 失败: {str(ex)[:80]}", flush=True)
        time.sleep(1)

    print(f"完成: 新增 {new_count}，累计 {len(existing)}", flush=True)

if __name__ == "__main__":
    main()
