# -*- coding: utf-8 -*-
"""test_acs_wait.py — 等待 Cloudflare 放行后重试下载。"""
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

# 等 Cloudflare（最多 60s，每 5s 检查）
for i in range(12):
    time.sleep(5)
    txt = ev("document.body.innerText") or ""
    if "安全验证" not in txt and "checking your browser" not in txt.lower():
        print(f"[{i*5}s] Cloudflare 放行!", flush=True)
        break
    print(f"[{i*5}s] 仍在验证...", flush=True)

txt = ev("document.body.innerText") or ""
print("页面:", txt[:120].replace("\n", " "))
print("URL:", ev("location.href"))

# 若放行，看是否有 PDF 查看器/下载链接
if "安全验证" not in txt:
    # 找 PDF 下载链接
    r = ev("""JSON.stringify(Array.from(document.querySelectorAll('a')).filter(a => /pdf|download|PDF/i.test((a.href||'')+(a.innerText||''))).map(a => a.href).slice(0,5))""")
    print("PDF 链接:", r)
ws.close()
