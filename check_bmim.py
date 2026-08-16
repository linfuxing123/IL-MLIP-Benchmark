# -*- coding: utf-8 -*-
"""check_bmim.py — 检查 BMIM-NTf2 数据。"""
import json
p = r"D:\Codex\MEC-Workspace\data\dft_bmim_ntf2.jsonl"
try:
    recs = [json.loads(l) for l in open(p, encoding="utf-8")]
    print("样本数:", len(recs))
    if recs:
        print("原子数:", set(r.get("natoms") for r in recs))
        es = [r["energy"] for r in recs]
        print(f"能量: {min(es):.4f} ~ {max(es):.4f} Ha")
        print("名称:", set(r.get("name") for r in recs))
except FileNotFoundError:
    print("文件不存在")
except json.JSONDecodeError as e:
    print("JSON 解析错误（可能正在写）:", e)
