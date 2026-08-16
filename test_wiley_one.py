# -*- coding: utf-8 -*-
"""test_wiley_one.py — 测试 Wiley 全文下载。"""
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

# Wiley 论文：10.1039/d6cp00608f 是 RSC；找一个 Wiley DOI（d6cp 是 RSC）
# 用 DB 里 Wiley 的（10.1002 前缀）
import sqlite3
db = sqlite3.connect(r"D:\Codex\MEC-Workspace\data\mec.db")
c = db.cursor()
c.execute("""SELECT doi, title, citations FROM chem_literature WHERE doi LIKE '10.1002/%' ORDER BY citations DESC LIMIT 3""")
for doi, title, cit in c.fetchall():
    print(f"候选 Wiley: {doi} [{cit}引] {title[:40]}")
db.close()
ws.close()
