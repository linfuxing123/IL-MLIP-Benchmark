# -*- coding: utf-8 -*-
"""check_progress.py — 查精读 + MACE 微调进度。"""
import sqlite3
import pathlib

db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("SELECT COUNT(*) FROM interpretations")
print("interpretations:", c.fetchone()[0])
c.execute("SELECT COUNT(*) FROM interpretations WHERE title LIKE 'arXiv:%'")
print("arXiv 精读:", c.fetchone()[0])
db.close()

mace_out = pathlib.Path(r"D:\Codex\MEC-Workspace\data\mace_finetune_out")
if mace_out.exists():
    files = list(mace_out.rglob("*"))
    print(f"\nMACE 输出目录: {len(files)} 文件")
    for f in files[:8]:
        print("  ", f.name, f.stat().st_size if f.is_file() else "dir")
else:
    print("\nMACE 输出目录未创建（训练可能还没开始/参数错误）")

# 检查 MACE 训练进程
import subprocess
r = subprocess.run(["powershell", "-Command", "Get-Process python | Select-Object Id,CPU"], capture_output=True, text=True)
print("\npython 进程:\n", r.stdout[:500])
