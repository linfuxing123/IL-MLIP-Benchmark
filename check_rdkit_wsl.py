# -*- coding: utf-8 -*-
"""check_rdkit_wsl.py — 测 WSL 里 rdkit 是否可用。"""
try:
    import rdkit
    print("rdkit", rdkit.__version__)
except ImportError:
    print("rdkit 未安装")
