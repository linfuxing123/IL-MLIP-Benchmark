#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""chem_review.py — 计算化学主题速览（CLI 工具，供 agent/用户调用）。

用法：python chem_review.py <关键词> [--top N] [--json]
按关键词在精读库+文献库检索，输出：相关论文数、核心论文（高引）、
近期趋势、精读摘要样本。
"""
import argparse
import json
import sqlite3
import sys

DB = r"D:\Codex\MEC-Workspace\data\mec.db"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("keyword", help="检索关键词（如 machine learning potential）")
    ap.add_argument("--top", type=int, default=5, help="核心论文数")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    kw = args.keyword
    like = f"%{kw}%"
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # 1. 文献库命中
    c.execute("SELECT COUNT(*) FROM chem_literature WHERE title LIKE ? OR abstract LIKE ?",
              (like, like))
    lit_n = c.fetchone()[0]

    # 2. 精读库命中
    c.execute("SELECT COUNT(*) FROM interpretations WHERE title LIKE ? OR summary_cn LIKE ? OR insights LIKE ?",
              (like, like, like))
    interp_n = c.fetchone()[0]

    # 3. 核心论文（高引，文献库）
    c.execute("""SELECT title, year, citations, venue FROM chem_literature
                 WHERE (title LIKE ? OR abstract LIKE ?) AND citations > 0
                 ORDER BY citations DESC LIMIT ?""", (like, like, args.top))
    core = [{"title": r[0], "year": r[1], "citations": r[2], "venue": r[3]} for r in c.fetchall()]

    # 4. 精读摘要样本
    c.execute("""SELECT title, summary_cn FROM interpretations
                 WHERE (title LIKE ? OR summary_cn LIKE ?) AND summary_cn != ''
                 ORDER BY id DESC LIMIT ?""", (like, like, args.top))
    samples = [{"title": r[0], "summary": (r[1] or "")[:200]} for r in c.fetchall()]

    conn.close()

    result = {
        "keyword": kw,
        "literature_hits": lit_n,
        "interpretation_hits": interp_n,
        "core_papers": core,
        "abstract_samples": samples,
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"主题: {kw}")
        print(f"文献库命中: {lit_n} | 精读库命中: {interp_n}")
        print(f"\n核心论文（高引）:")
        for p in core:
            print(f"  [{p['citations']}引, {p['year']}] {p['title'][:70]}")
        print(f"\n精读摘要样本:")
        for s in samples:
            print(f"  ▶ {s['title'][:50]}")
            print(f"    {s['summary'][:100]}...")

if __name__ == "__main__":
    main()
