# -*- coding: utf-8 -*-
"""test_acs_one.py — 测试单篇 ACS 全文下载（验证登录态）。"""
import json
import pathlib
import sys
import time
import urllib.request
import websocket

PORT = 9224
OUT_DIR = pathlib.Path(r"D:\文献\chem-fulltext")
OUT_DIR.mkdir(parents=True, exist_ok=True)

tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json").read())
page = next(t for t in tabs if t["type"] == "page")
ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=180)
_id = [0]

def send(method, params=None, timeout=120):
    _id[0] += 1
    mid = _id[0]
    ws.send(json.dumps({"id": mid, "method": method, "params": params or {}}))
    while True:
        ws.settimeout(timeout)
        msg = json.loads(ws.recv())
        if msg.get("id") == mid:
            return msg.get("result", {})

def ev(expr):
    r = send("Runtime.evaluate", {"expression": expr, "returnByValue": True})
    return r.get("result", {}).get("value")

send("Page.enable")
send("DOM.enable")
send("Page.setDownloadBehavior", {"behavior": "allow", "downloadPath": str(OUT_DIR)})

# 测试：The Potential of Neural Network Potentials (51引)
doi = "10.1021/acsphyschemau.4c00004"
url = f"https://pubs.acs.org/doi/pdf/{doi}"
print("导航:", url)
send("Page.navigate", {"url": url})
time.sleep(20)

# 检查页面状态
txt = ev("document.body.innerText") or ""
print("页面文本片段:", txt[:150].replace("\n", " "))
print("URL:", ev("location.href"))

# 检查下载目录
import glob, os
files = glob.glob(str(OUT_DIR / "*"))
print("下载目录:", files)
if files:
    for f in files:
        print("  ", os.path.basename(f), os.path.getsize(f), "bytes")
ws.close()
