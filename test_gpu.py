# -*- coding: utf-8 -*-
"""test_gpu.py — 测试 torch CUDA 是否可用。"""
import torch

print("torch:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
print("CUDA 版本:", torch.version.cuda)
if torch.cuda.is_available():
    print("设备:", torch.cuda.get_device_name(0))
    print("显存: %.1f GB" % (torch.cuda.get_device_properties(0).total_memory / 1e9))
    # 实际跑个小 tensor 测试（之前报 unknown error）
    try:
        x = torch.randn(1000, 1000, device="cuda")
        y = x @ x
        print("CUDA 矩阵运算 OK:", y.sum().item())
        # 释放
        del x, y
        torch.cuda.empty_cache()
        print("CUDA 实际可用 ✅")
    except Exception as e:
        print("CUDA 运算失败:", str(e)[:150])
else:
    print("CUDA 不可用")
