#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""interpret_pdf.py — DeepSeek 精读：PDF → 结构化入 interpretations 表（适配旧表结构）。

旧表列：lit_id/title/journal/year/doi/summary_cn/method/results/insights/relevance/status
"""
import argparse
import pathlib
import re
import sqlite3

DB = r"D:\Codex\MEC-Workspace\data\mec.db"

def extract_text(pdf_path):
    import pdfplumber
    text_parts = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            t = page.extract_text() or ""
            text_parts.append(f"--- page {i+1} ---\n{t}")
    return "\n".join(text_parts)

def structure(text):
    """全文定位式分段：找章节标题行的绝对位置切分（对双栏也有效）。"""
    sections = {"abstract": "", "methods": "", "results": "", "conclusion": "", "rest": ""}
    lines = text.split("\n")
    # 找标题行索引
    markers = {}
    for i, line in enumerate(lines):
        low = line.lower().strip()
        if re.match(r"^\s*(\d+[.\s]*)?abstract\b", low) and len(low) < 30 and "abstract" not in markers:
            markers["abstract"] = i
        elif re.match(r"^\s*(\d+[.\s]*)?(methods?|methodology|computational details|theory)\b", low) and len(low) < 40 and "methods" not in markers:
            markers["methods"] = i
        elif re.match(r"^\s*(\d+[.\s]*)?(results? and discussion|results?)\b", low) and len(low) < 40 and "results" not in markers:
            markers["results"] = i
        elif re.match(r"^\s*(\d+[.\s]*)?(conclusions?|summary and outlook)\b", low) and len(low) < 40 and "conclusion" not in markers:
            markers["conclusion"] = i
    # 边界排序切分
    bounds = sorted(markers.items(), key=lambda kv: kv[1])
    for j, (name, start) in enumerate(bounds):
        end = bounds[j + 1][1] if j + 1 < len(bounds) else len(lines)
        sections[name] = "\n".join(lines[start:end])
    # 摘要之前算 rest
    if bounds:
        sections["rest"] = "\n".join(lines[:bounds[0][1]])
    return sections

def extract_numbers(text, limit=12):
    pattern = re.compile(
        r"(\d+\.?\d*\s*(?:eV|kcal/mol|meV|Å|kJ/mol|Hartree|cm⁻¹|cm-1|fs|ps|ns|meV/Å|K|GB|MB|s))\b",
        re.IGNORECASE)
    found = pattern.findall(text)
    seen, out = set(), []
    for n in found:
        key = n.lower()
        if key not in seen:
            seen.add(key)
            out.append(n)
    return out[:limit]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pdf", help="PDF 路径")
    ap.add_argument("--title", default="")
    ap.add_argument("--doi", default="")
    ap.add_argument("--journal", default="arXiv")
    ap.add_argument("--year", default="")
    ap.add_argument("--lit-id", default=None, type=int)
    ap.add_argument("--relevance", default="计算化学前沿")
    args = ap.parse_args()

    pdf_path = pathlib.Path(args.pdf)
    if not pdf_path.exists():
        print(f"文件不存在: {pdf_path}")
        return

    text = extract_text(pdf_path)
    secs = structure(text)
    numbers = extract_numbers(text)

    title = args.title or " ".join(text.split("\n")[:3])[:200]
    summary_cn = (secs["abstract"].strip()[:1500] or text[:500])
    method_cn = secs["methods"].strip()[:1500]
    results_cn = secs["results"].strip()[:1500]
    insights_cn = f"关键数值: {numbers}\n结论: {secs['conclusion'].strip()[:800]}"

    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""INSERT INTO interpretations
        (lit_id, title, journal, year, doi, summary_cn, method, results, insights, relevance, status)
        VALUES (?,?,?,?,?,?,?,?,?,?, '已解读')""",
        (args.lit_id, title[:500], args.journal, args.year, args.doi,
         summary_cn, method_cn, results_cn, insights_cn, args.relevance))
    conn.commit()
    c.execute("SELECT COUNT(*) FROM interpretations WHERE status='已解读'")
    print(f"已入库（已解读总数 {c.fetchone()[0]}）")
    conn.close()

    print(f"\n标题: {title[:80]}")
    print(f"摘要: {summary_cn[:120]}...")
    print(f"方法节: {len(secs['methods'])} 字符 | 结果节: {len(secs['results'])} 字符")
    print(f"关键数值: {numbers}")

if __name__ == "__main__":
    main()
