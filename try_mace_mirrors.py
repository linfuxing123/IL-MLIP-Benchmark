# -*- coding: utf-8 -*-
"""try_mace_mirrors.py — 多镜像源重试下载 MACE-MP-0 权重。

源列表（按优先级）：
1. ghproxy 类镜像（ghproxy.com / gh-proxy.com / mirror.ghproxy.com）
2. jsdelivr CDN（GitHub 文件可经 jsdelivr 走）
3. fastgit / hub.fastgit
4. 直连 github（最后再试）
"""
import pathlib
import urllib.request

TARGET = "2023-12-10-mace-128-L0_energy_epoch-249.model"
OUT = pathlib.Path(r"D:\Codex\MEC-Workspace\data\mace_mp0_small.model")
EXPECTED_MIN = 30_000_000  # 32.6MB，至少 30MB 才算成功

SOURCES = [
    # ghproxy 系列
    f"https://ghproxy.com/https://github.com/ACEsuit/mace-mp/releases/download/mace_mp_0/{TARGET}",
    f"https://gh-proxy.com/https://github.com/ACEsuit/mace-mp/releases/download/mace_mp_0/{TARGET}",
    f"https://mirror.ghproxy.com/https://github.com/ACEsuit/mace-mp/releases/download/mace_mp_0/{TARGET}",
    # jsdelivr（GitHub 大文件可能不支持 release，但试）
    f"https://cdn.jsdelivr.net/gh/ACEsuit/mace-mp@{'mace_mp_0'}/{TARGET}",
    # fastgit
    f"https://hub.fastgit.xyz/ACEsuit/mace-mp/releases/download/mace_mp_0/{TARGET}",
    # 直连
    f"https://github.com/ACEsuit/mace-mp/releases/download/mace_mp_0/{TARGET}",
]

def try_download(url, timeout=60):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = resp.read()
        return data
    except Exception as ex:
        return None

def main():
    for i, url in enumerate(SOURCES):
        print(f"[{i+1}/{len(SOURCES)}] 试: {url[:80]}...", flush=True)
        data = try_download(url)
        if data and len(data) > EXPECTED_MIN:
            OUT.write_bytes(data)
            print(f"  ✅ 成功！{len(data)/1024/1024:.1f} MB → {OUT}", flush=True)
            return True
        elif data:
            print(f"  ⚠️ 太小 {len(data)} bytes（失败）", flush=True)
        else:
            print(f"  ✗ 失败", flush=True)
    print("全部失败", flush=True)
    return False

if __name__ == "__main__":
    main()
