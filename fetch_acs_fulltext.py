# -*- coding: utf-8 -*-
"""fetch_acs_fulltext.py — 用 ACS 登录态抓高引 ACS 论文全文。

通过 CDP 浏览器（保留登录 cookies）访问 ACS 论文页面并触发 PDF 下载。
ACS PDF URL 模式：https://pubs.acs.org/doi/pdf/<doi>
"""
import json
import pathlib
import sqlite3
import sys
import time
import urllib.request
import websocket

PORT = 9224
DB = r"D:\Codex\MEC-Workspace\data\mec.db"
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

def main():
    db = sqlite3.connect(DB)
    c = db.cursor()
    c.execute("""SELECT doi, title, citations FROM chem_literature
                 WHERE doi LIKE '10.1021/%' ORDER BY citations DESC LIMIT 8""")
    papers = c.fetchall()
    print(f"ACS 高引论文: {len(papers)}", flush=True)

    for doi, title, cit in papers:
        safe = doi.replace("/", "_").replace(".", "_")
        pdf_path = OUT_DIR / f"acs_{safe}.pdf"
        if pdf_path.exists():
            print(f"跳过: {doi}", flush=True)
            continue
        url = f"https://pubs.acs.org/doi/pdf/{doi}"
        print(f"访问: {doi} [{cit}引]", flush=True)
        send("Page.navigate", {"url": url})
        time.sleep(15)
        # 检查下载（Page.setDownloadBehavior 自动存到目录）
        import glob
        files = glob.glob(str(OUT_DIR / "*.pdf")) + glob.glob(str(OUT_DIR / "*.crdownload"))
        newest = max(files, key=lambda f: pathlib.Path(f).stat().st_mtime) if files else None
        if newest and "acs_" in newest:
            print(f"✓ 下载: {pathlib.Path(newest).name}", flush=True)
        else:
            txt = ev("document.body.innerText") or ""
            if "denied" in txt.lower() or "access" in txt.lower() and "no" in txt.lower():
                print(f"✗ 无权限: {doi}", flush=True)
            else:
                print(f"? 状态: {txt[:60]}", flush=True)
        time.sleep(2)

    db.close()
    ws.close()

if __name__ == "__main__":
    main()
