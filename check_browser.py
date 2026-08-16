# -*- coding: utf-8 -*-
"""check_browser.py — 检查 Edge CDP 状态 + 登录 cookies。"""
import json
import urllib.request
import websocket

PORT = 9224
try:
    tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json").read())
    pages = [t for t in tabs if t["type"] == "page"]
    print(f"CDP 9224 在线，{len(pages)} 个页面")
    for p in pages[:3]:
        print("  ", p.get("url", "")[:80])
except Exception as ex:
    print(f"CDP 不可达: {str(ex)[:60]}")
    exit(1)

# 检查 cookies
page = pages[0] if pages else None
if page:
    ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=60)
    ws.send(json.dumps({"id": 1, "method": "Network.getAllCookies"}))
    while True:
        m = json.loads(ws.recv())
        if m.get("id") == 1:
            cookies = m.get("result", {}).get("cookies", [])
            from collections import Counter
            domains = Counter(c["domain"] for c in cookies)
            print(f"\n总 cookies: {len(cookies)}")
            for key in ["publish.acs.org", "onlinelibrary.wiley.com", ".acs.org", ".wiley.com", ".rsc.org"]:
                n = sum(1 for c in cookies if key in c["domain"])
                print(f"  {key}: {n}")
            break
    ws.close()
