# -*- coding: utf-8 -*-
"""get_all_cookies.py — CDP Network.getAllCookies 查登录态。"""
import json
import urllib.request
import websocket

PORT = 9224
tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json").read())
page = next(t for t in tabs if t["type"] == "page")
ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=60)

ws.send(json.dumps({"id": 1, "method": "Network.getAllCookies"}))
while True:
    m = json.loads(ws.recv())
    if m.get("id") == 1:
        cookies = m.get("result", {}).get("cookies", [])
        # 按域分组统计
        from collections import Counter
        domains = Counter(c["domain"] for c in cookies)
        print("cookies 总数:", len(cookies))
        for d, n in domains.most_common(15):
            print(f"  {d}: {n}")
        # 检查关键登录域
        for key in ["publish.acs.org", "pubs.rsc.org", "onlinelibrary.wiley.com", "acs.org", ".rsc.org", "wiley.com"]:
            hits = [c for c in cookies if key in c["domain"]]
            print(f"\n{key}: {len(hits)} cookies")
            for c in hits[:3]:
                print(f"    {c['name']}={c['value'][:20]}...")
        break
ws.close()
