# -*- coding: utf-8 -*-
"""probe_publisher_access.py — 用 CDP 浏览器（含登录 cookies）探测各出版商访问性。

关键：用浏览器上下文 fetch（自动带 cookies），测 ACS/Wiley/RSC 全文页
是否 Cloudflare 拦截。若拦截，记录；若通，直接抓。
"""
import json
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

# 用浏览器 fetch（带 cookies）测各站
targets = [
    ("ACS", "https://pubs.acs.org/doi/10.1021/acs.jpcb.3c05928"),
    ("Wiley", "https://onlinelibrary.wiley.com/doi/10.1002/asia.202300684"),
    ("RSC", "https://pubs.rsc.org/en/content/articlelanding/2026/cp/d6cp00608f"),
]
for name, url in targets:
    r = ev(f"""JSON.stringify(await (async () => {{
      try {{
        const res = await fetch('{url}', {{credentials: 'include', redirect: 'follow'}});
        const txt = await res.text();
        const blocked = txt.includes('安全验证') || txt.includes('checking your browser') || txt.includes('Just a moment');
        return {{status: res.status, len: txt.length, blocked}};
      }} catch(e) {{ return {{err: e.message.slice(0,60)}}; }}
    }})())""")
    print(f"{name}: {r}", flush=True)
ws.close()
