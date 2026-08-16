# -*- coding: utf-8 -*-
"""test_wiley_dl.py — 实际测试 Wiley PDF 下载。"""
import json
import pathlib
import sys
import time
import urllib.request
import websocket

PORT = 9224
OUT_DIR = pathlib.Path(r"D:\文献\chem-fulltext")

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

doi = "10.1002/asia.202300684"
url = f"https://onlinelibrary.wiley.com/doi/pdf/{doi}"
print("导航:", url)
send("Page.navigate", {"url": url})
time.sleep(20)

txt = ev("document.body.innerText") or ""
print("页面:", txt[:100].replace("\n", " "))
print("URL:", ev("location.href"))

import glob, os
files = glob.glob(str(OUT_DIR / "*"))
new = [f for f in files if os.path.basename(f) not in ["arxiv_2206.07697.pdf"]]
print("新下载:", new)
ws.close()
