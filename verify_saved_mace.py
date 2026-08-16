# -*- coding: utf-8 -*-
"""verify_saved_mace.py — 验证已保存的 MACE 微调模型。"""
import json
import pathlib

import numpy as np

# 检查已保存模型
model_dir = pathlib.Path(r"D:\Codex\MEC-Workspace\data\mace_finetune_single")
models = list(model_dir.rglob("*.model")) if model_dir.exists() else []
print(f"单 IL 微调模型: {len(models)} 个")
for m in models:
    print(f"  {m.name} ({m.stat().st_size/1024/1024:.1f} MB)")

model_dir2 = pathlib.Path(r"D:\Codex\MEC-Workspace\data\mace_finetune_all")
models2 = list(model_dir2.rglob("*.model")) if model_dir2.exists() else []
print(f"\n多组分微调模型: {len(models2)} 个")
for m in models2[:3]:
    print(f"  {m.name} ({m.stat().st_size/1024/1024:.1f} MB)")

# 数据统计总览
il_files = {
    "EMIM-BF4 原始": r"D:\Codex\MEC-Workspace\data\dft_il_rdkit.jsonl",
    "EMIM-BF4 补充": r"D:\Codex\MEC-Workspace\data\dft_emim_bf4_more.jsonl",
    "BMIM-NTf2": r"D:\Codex\MEC-Workspace\data\dft_bmim_ntf2.jsonl",
    "批量(3 IL)": r"D:\Codex\MEC-Workspace\data\dft_il_batch.jsonl",
}
print("\nIL 数据总览:")
total = 0
for name, p in il_files.items():
    fp = pathlib.Path(p)
    if fp.exists():
        n = sum(1 for _ in fp.open(encoding="utf-8"))
        total += n
        print(f"  {name}: {n}")
print(f"  总计: {total} IL 样本")
