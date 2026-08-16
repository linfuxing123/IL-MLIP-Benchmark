# -*- coding: utf-8 -*-
"""check_login_status.py — 检查各出版商登录态。"""
import json
import sys
import time
import urllib.request
import websocket

PORT = 9224
tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json").read())
page = next(t for t in tabs if t["type"] == "page")
ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=60)

def ev(expr):
    ws.send(json.dumps({"id": 1, "method": "Runtime.evaluate",
                        "params": {"expression": expr, "returnByValue": True}}))
    while True:
        m = json.loads(ws.recv())
        if m.get("id") == 1:
            return m["result"]["result"].get("value")

# 检查 cookies（publish.acs.org / pubs.rsc.org / onlinelibrary.wiley.com）
for domain in ["publish.acs.org", "pubs.rsc.org", "onlinelibrary.wiley.com", "acs.org", "rsc.org"]:
    r = ev(f"JSON.stringify(await (async () => {{ try {{ const c = await cookieStore.getAll({{domain: '{domain}'}}); return c.length; }} catch(e) {{ return 'err:'+e.message.slice(0,40); }} }})())")
    print(f"{domain}: {r} cookies")

# 用 fetch 探测各站是否登录（看返回是否含登录标志）
for url in ["https://publish.acs.org/", "https://pubs.rsc.org/"]:
    r = ev(f"JSON.stringify(await (async () => {{ try {{ const res = await fetch('{url}', {{credentials: 'include'}}); return res.status; }} catch(e) {{ return 'err:'+e.message.slice(0,40); }} }})())")
    print(f"fetch {url}: {r}")
ws.close()
