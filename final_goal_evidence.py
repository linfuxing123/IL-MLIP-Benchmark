# -*- coding: utf-8 -*-
"""final_goal_evidence.py — 电解质 MLIP 目标最终证据。"""
import json
import pathlib
import sqlite3

print("=== 数据集资产 ===")
data_files = {
    "dft_h2o.jsonl": "H2O 50 几何",
    "dft_multimol.jsonl": "CH4/NH3/H2O/HF 120",
    "dft_ions.jsonl": "BF4-/PF6-/NO3-/NH4+ 80",
    "dft_il_rdkit.jsonl": "EMIM-BF4 30",
    "dft_bmim_ntf2.jsonl": "BMIM-NTf2 15",
    "dft_il_batch.jsonl": "批量生成中(21/120)",
}
total = 0
for f, desc in data_files.items():
    p = pathlib.Path(r"D:\Codex\MEC-Workspace\data") / f
    if p.exists():
        n = sum(1 for _ in p.open(encoding="utf-8"))
        total += n
        print(f"  {f}: {n} 条 ({desc})")
    else:
        print(f"  {f}: 未创建 ({desc})")
print(f"  总计: {total} 样本")

print("\n=== 模型资产 ===")
for m in ["mlip_general_h2o.pt", "mlip_multimol.pt", "mlip_ions.pt", "mlip_il_schnet.pt"]:
    p = pathlib.Path(r"D:\Codex\MEC-Workspace\data") / m
    print(f"  {m}: {'✓' if p.exists() else '✗'}")

print("\n=== 报告 ===")
for r in ["REPORT_ELECTROLYTE_MLIP_METHODS.md", "REPORT_ELECTROLYTE_MLIP.md", "PLAN_ELECTROLYTE_MLIP.md"]:
    p = pathlib.Path(r"D:\Codex\MEC-Workspace\workspace\chem-library") / r
    print(f"  {r}: {'✓' if p.exists() else '✗'}")

print("\n=== mec.db 成果 ===")
db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("SELECT COUNT(*) FROM papers WHERE doi='mlip-electrolyte-2026'")
print("  论文记录:", c.fetchone()[0])
c.execute("SELECT COUNT(*) FROM achievements WHERE paper='mlip-electrolyte-2026'")
print("  成果记录:", c.fetchone()[0])
db.close()
