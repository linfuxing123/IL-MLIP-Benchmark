# -*- coding: utf-8 -*-
"""register_daily_task.py — 注册 Windows 计划任务：每日自动增量更新。

用法：python register_daily_task.py [--enable] [--disable]
默认注册每日 09:00 运行 incremental_update.py（抓 PDF + 精读）。
"""
import subprocess
import sys

PY = r"D:\Codex\.cache\codex-runtimes\mec-lit-venv\Scripts\python.exe"
SCRIPT = r"D:\Codex\MEC-Workspace\workspace\chem-library\incremental_update.py"
TASK_NAME = "MEC-ChemLibrary-Daily"

def register():
    cmd = [
        "schtasks", "/Create", "/TN", TASK_NAME, "/TR",
        f'"{PY}" "{SCRIPT}" --days 7 --fetch-pdf --interpret',
        "/SC", "DAILY", "/ST", "09:00", "/F",
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print("stdout:", r.stdout.strip())
    print("stderr:", r.stderr.strip())
    print("rc:", r.returncode)

def disable():
    r = subprocess.run(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"],
                       capture_output=True, text=True)
    print("删除:", r.stdout.strip() or r.stderr.strip())

def query():
    r = subprocess.run(["schtasks", "/Query", "/TN", TASK_NAME, "/V", "/FO", "LIST"],
                       capture_output=True, text=True)
    # 提取关键行
    for line in (r.stdout or "").splitlines():
        if any(k in line for k in ["TaskName", "Status", "Next Run Time", "Schedule", "Task To Run"]):
            print(line.strip())

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--disable":
        disable()
    elif len(sys.argv) > 1 and sys.argv[1] == "--query":
        query()
    else:
        register()
        query()
