#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""arxiv_fetch.py — 从 arXiv API 全自动采集计算化学前沿论文。

查询词覆盖计算化学博士级方向：
  - quantum chemistry / DFT / ab initio / wavefunction
  - machine learning potential / neural network potential / ML force field
  - QM/MM / molecular dynamics / reaction mechanism
  - density functional theory / exchange-correlation
输出：D:\Codex\MEC-Workspace\data\chem_literature.jsonl（增量追加，按 id 去重）
"""
import json
import pathlib
import time
import urllib.parse
import urllib.request

OUT = pathlib.Path(r"D:\Codex\MEC-Workspace\data\chem_literature.jsonl")
BASE = "http://export.arxiv.org/api/query"

# 计算化学核心主题查询（博士级覆盖）
QUERIES = [
    # 量子化学方法
    'cat:physics.chem-ph AND (all:"coupled cluster" OR all:"MP2" OR all:"quantum chemistry")',
    'cat:physics.chem-ph AND all:"density functional theory"',
    'cat:physics.chem-ph AND all:"wavefunction" AND all:"ab initio"',
    # ML 势函数
    'cat:physics.chem-ph AND (all:"machine learning potential" OR all:"neural network potential" OR all:"ML force field")',
    'cat:physics.chem-ph AND all:"deep learning" AND all:"molecular dynamics"',
    # QM/MM 与反应机理
    'cat:physics.chem-ph AND all:"QM/MM"',
    'cat:physics.chem-ph AND all:"reaction mechanism" AND all:"transition state"',
    # 光谱与电子结构
    'cat:physics.chem-ph AND all:"spectroscopy" AND all:"excited state"',
    'cat:physics.chem-ph AND all:"GW" AND all:"band gap"',
    # 分子动力学
    'cat:physics.chem-ph AND all:"molecular dynamics" AND all:"force field"',
]

def fetch(query, start=0, max_results=50):
    params = urllib.parse.urlencode({
        "search_query": query,
        "start": start,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    })
    url = f"{BASE}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": "MEC-chem-library/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read().decode("utf-8")

def parse_atom(text, tag):
    start = text.find(f"<{tag}>")
    if start < 0:
        return None
    end = text.find(f"</{tag}>", start)
    if end < 0:
        return None
    return text[start + len(tag) + 2:end]

def parse_entries(xml):
    """极简 XML 解析（arXiv API 返回固定结构）"""
    entries = []
    for block in xml.split("<entry>"):
        if not block.strip():
            continue
        e = {}
        e["id"] = parse_atom(block, "id")
        e["title"] = parse_atom(block, "title")
        e["summary"] = parse_atom(block, "summary")
        e["published"] = parse_atom(block, "published")
        e["updated"] = parse_atom(block, "updated")
        # authors
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
        # categories
        cats = []
        idx = 0
        while True:
            a = block.find('term="', idx)
            if a < 0:
                break
            ae = block.find('"', a + 6)
            cats.append(block[a + 6:ae])
            idx = ae + 1
        e["categories"] = [c for c in cats if c.startswith("physics.chem-ph") or c.startswith("cond-mat") or c.startswith("cs.")]
        e["source"] = "arxiv"
        # 过滤 feed 元数据误当 entry（title 以 "arXiv Query" 开头的是查询描述）
        if e["id"] and e["title"] and not e["title"].strip().startswith("arXiv Query"):
            entries.append(e)
    return entries

def main():
    existing = set()
    if OUT.exists():
        for line in OUT.open(encoding="utf-8"):
            try:
                d = json.loads(line)
                existing.add(d.get("id"))
            except Exception:
                pass
    print(f"已有记录: {len(existing)}", flush=True)

    new_count = 0
    for qi, query in enumerate(QUERIES):
        try:
            xml = fetch(query, 0, 40)
            entries = parse_entries(xml)
            with OUT.open("a", encoding="utf-8") as f:
                for e in entries:
                    eid = e["id"]
                    if eid in existing:
                        continue
                    # 清理标题
                    e["title"] = " ".join((e["title"] or "").split())
                    f.write(json.dumps(e, ensure_ascii=False) + "\n")
                    existing.add(eid)
                    new_count += 1
            print(f"[{qi+1}/{len(QUERIES)}] {query[:50]}... +{sum(1 for e in entries if e['id'] in existing and True)} 候选", flush=True)
        except Exception as ex:
            print(f"[{qi}] 查询失败: {query[:40]} → {ex}", flush=True)
        time.sleep(1)

    print(f"完成: 新增 {new_count} 篇，累计 {len(existing)} 篇", flush=True)

if __name__ == "__main__":
    main()
