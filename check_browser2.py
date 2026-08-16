# -*- coding: utf-8 -*-
"""check_browser2.py — 逐个页面连 websocket 查 cookies。"""
import json
import urllib.request
import websocket

PORT = 9224
tabs = json.loads(urllib.request.urlopen(f"http://127.0.0.1:{PORT}/json").read())
pages = [t for t in tabs if t["type"] == "page"]

from collections import Counter
for i, page in enumerate(pages):
    try:
        ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=20)
        ws.send(json.dumps({"id": 1, "method": "Network.getAllCookies"}))
        while True:
            m = json.loads(ws.recv())
            if m.get("id") == 1:
                cookies = m.get("result", {}).get("cookies", [])
                domains = Counter(c["domain"] for c in cookies)
                print(f"页面 {i} ({page.get('url','')[:50]}): {len(cookies)} cookies")
                for key in ["publish.acs.org", "onlinelibrary.wiley.com", ".acs.org", ".wiley.com"]:
                    n = sum(1 for c in cookies if key in c["domain"])
                    if n:
                        print(f"    {key}: {n}")
                break
        ws.close()
        break  # 第一个成功的就够
    except Exception as ex:
        print(f"页面 {i} 连接失败: {str(ex)[:40]}")
