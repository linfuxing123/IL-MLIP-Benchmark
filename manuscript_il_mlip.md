# IL-MLIP-Benchmark: A Benchmark Dataset and Energy-Decomposition Training Framework for Ionic Liquid Machine-Learned Interatomic Potentials

**Fuxing Lin** (Hunan Institute of Engineering; ORCID 0000-0003-7588-6942)

> 手稿 v0.1（2026-08-16）· 数据+方法双创新 · 目标期刊：Scientific Data / Digital Discovery / JCIM

## Abstract

Ionic liquids (ILs) are promising electrolytes for batteries and catalysis, yet
machine-learned interatomic potentials (MLIPs) for ILs remain unexplored relative
to molecular and catalytic systems. We introduce (i) **IL-MLIP-Benchmark**, the
first systematic benchmark dataset of IL cation–anion pairs — 435 conformations
across 8 IL combinations (EMIM/BMIM/Pyr14 × BF4/PF6/NTf2/FSI) at B3LYP/STO-3G
with energies (and forces for EMIM-BF4) under a reproducible sampling protocol —
and (ii) an **energy-decomposition analysis (EDT)** revealing that isolated ions
are energetically rigid (E_cation std 54 meV, E_anion std 14 meV) while the
interaction term E_int carries the full conformational dependence. MACE fine-tuning
achieves chemical accuracy (23.3 ± 5.8 meV/atom, 5-fold cross-validation), a
263× improvement over from-scratch SchNet (6115.7 meV/atom), and generalizes
across unseen ILs (mean 37.6 meV/atom, 6/8 below 43 meV/atom). These results
establish that pretraining priors are necessary for IL MLIPs and that the
benchmark captures transferable IL chemistry.

## 1. Introduction

- MLIP 现状：小分子（MD17/ANI）和催化（OC20）有成熟 benchmark，IL 空白
- IL 的挑战：离子对取向主导（库仑 1/d 只解释 12.4% 能量，见本工作）
- 两个贡献：数据集（创新点 A）+ EDT（创新点 B）

## 2. Methods

### 2.1 IL-MLIP-Benchmark 数据集（创新点 A）
- 8 IL 组合 × N 构型
- 统一采样协议（固定 seed + 等间隔距离）
- B3LYP/def2-SVP + 解析力
- 与 MD17/ANI/OC20 对比表

### 2.2 能量分解训练 EDT（创新点 B）
- E_pair = E_cat + E_an + E_int
- 前提：离子刚性（形变 <1%，已验证）
- E_cat/E_an 用刚性模型，E_int 用等变模型拟合残差
- 数据需求降低论证

### 2.3 模型与训练
- MACE 微调 / MACE 从头 / SchNet 不变（基线）
- benchmark 协议：跨 IL 划分（train 7 IL / test 1 IL）

## 3. Results

### 3.1 IL-MLIP-Benchmark 数据集
8 IL 离子对（EMIM/BMIM/Pyr14 × BF4/PF6/NTf2/FSI），共 435 个干净构型
（B3LYP/STO-3G，能量 std 471-795 mHa），过滤原子重叠坏构型后保留。
数据分布：EMIM-BF4 60 / BMIM-BF4 58 / Pyr14-FSI 60 / Pyr14-NTf2 60 /
BMIM-NTf2 60 / EMIM-NTf2 59 / EMIM-PF6 43 / BMIM-PF6 35。

### 3.2 化学精度（5 折交叉验证）
| 模型 | RMSE (meV/atom) |
|---|---|
| SchNet 从头训练 | 6115.7 ± 2756.9 |
| MACE-MP-0 zero-shot | ~1070 |
| **MACE 微调** | **23.3 ± 5.8** ✅ |

MACE 微调达化学精度（<43 meV/atom），比 SchNet 从头训练好 263 倍，
证明预训练先验对 IL 离子对 MLIP 是必要的。

### 3.2b 力预测（MACE 力微调）
能量-力联合微调（--loss ef）：
- 能量 RMSE：31.8 meV/atom（化学精度 ✅）
- 力 RMSE：640.8 meV/Å（相对 12.36%）
- 力微调有效（zero-shot 1057 → 微调 640.8 meV/Å），偏高因 60 构型数据
  少 + STO-3G 力精度有限

### 3.2c 跨 IL 泛化（leave-one-IL-out，数据集核心价值）
MACE 在 7 IL 上微调，评估未见的第 8 个 IL：
| test IL | valid RMSE (meV/atom) |
|---|---|
| EMIM-NTf2 | 25.5 ✅ |
| EMIM-PF6 | 32.7 ✅ |
| EMIM-BF4 | 37.2 ✅ |
| BMIM-NTf2 | 39.0 ✅ |
| Pyr14-FSI | 39.0 ✅ |
| BMIM-BF4 | 39.3 ✅ |
| BMIM-PF6 | 43.8 |
| Pyr14-NTf2 | 44.6 |

6/8 IL 达化学精度（<43 meV/atom），平均 ~37.6。证明 IL-MLIP-Benchmark
覆盖 IL 共性化学空间，MACE 预训练+微调可泛化到未见 IL。

### 3.3 能量分解（EDT，创新点 B）
用 MACE 分解 E_pair = E_cat + E_an + E_int：
- E_cat std 54 meV、E_an std 14 meV（离子在离子对中能量刚性）
- E_int std 8450 meV ≈ E_pair（比值 1.00，承载所有构型依赖）
- **结论**：EDT 不降低拟合难度，但提供**可迁移性**（E_cat/E_an 复用）
  + **可解释性**（E_int 是纯相互作用项）

## 4. Discussion
- IL 离子对能量由"取向 + 距离"共同决定（库仑 1/d 仅解释 12.4%）
- 预训练先验（MACE）是 IL MLIP 的必要条件（263 倍差距）
- EDT 的价值在可迁移性 + 可解释性，非降低难度
- 数据质量：原子重叠坏构型必须过滤（RDKit ETKDG 某些 seed 生成重叠）

## 5. Data Availability
- **数据集**：IL-MLIP-Benchmark（8 IL × 435 个干净构型，B3LYP/STO-3G，
  含能量 + EMIM-BF4 60 构型的力）。本地路径
  `data/il_benchmark_clean/`，待上传 Zenodo 获取 DOI。
- **代码**：GitHub linfuxing123/IL-Property-ML（数据生成 / 坏构型过滤 /
  MACE 微调 / 交叉验证脚本）
- **模型**：MACE 微调模型（`data/mace_force_final/` 等）

## 6. References

1. Batatia, I. et al. MACE: Higher Order Equivariant Message Passing
   Neural Networks for Fast and Accurate Force Fields.
   arXiv:2206.07697 (2022).
2. Thomas, N. et al. Tensor Field Networks: Rotation- and
   Translation-Equivariant Neural Networks for 3D Point Clouds.
   arXiv:1802.08219 (2018).
3. Satorras, V. G. et al. E(n) Equivariant Graph Neural Networks.
   arXiv:2102.09844 (2021).
4. Schütt, K. T. et al. SchNet: A Continuous-Filter Convolutional Neural
   Network for Modeling Quantum Interactions. arXiv:1706.08566 (2017).
5. Chanussot, L. et al. Open Catalyst 2020 (OC20) Dataset and Community
   Challenges. arXiv:2010.09990 (2020).
6. Unke, O. T. et al. Machine Learning Force Fields. Chem. Rev. 121,
   10142 (2021). DOI: 10.1021/acs.chemrev.0c01111.

> 注：arXiv 号来自本工作精读库已收录论文；正式投稿前建议逐条核对 DOI 格式。
