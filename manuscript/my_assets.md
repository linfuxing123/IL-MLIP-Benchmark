# 蔺复兴（Lin Fuxing）— 科研资产清单

## 一、联系方式
- **姓名**：蔺复兴（Lin Fuxing）
- **单位**：湖南工程学院（Hunan Institute of Engineering，HIE）
- **邮箱**：3612411485@qq.com
- **ORCID**：0009-0003-7588-6942
- **GitHub**：github.com/linfuxing123

## 二、GitHub 仓库
### 1. IL-MLIP-Benchmark（主仓库）— github.com/linfuxing123/IL-MLIP-Benchmark
首个人工智能机器学习原子间势（MLIP）的离子液体基准数据集。

**数据**（data/）：
- 8 个 IL 的构型（JSONL）：EMIM/BMIM/Pyr14 × BF4/PF6/NTf2/FSI = 8 个（435 构型，B3LYP/STO-3G 能量+力）
- `il_force/*_force.xyz`：8 IL 每原子力数据（60 帧/IL）
- 体相数据：bulk 2-ion-pair EMIM-BF4（59 帧 / 86 帧 v6）
- `force_8il_comparison.json`：8 IL 力对比（3-seed l0/l2 32ch）

**lc_equivariance/**（等变量化定律）：
- `learning_curve_results.json`：学习曲线（Pyr14 32/128ch、EMIM 128ch）
- `force_radial_8il.json`：8 IL 力径向占比
- `seed_extension.json`：seed 扩展
- 7 张图：quantitative_laws_fig/fig2/fig3/overview + unified_law_fig/support/beta/mechanism

**manuscript/**：论文稿件（含统一律）+ 推导 + 叙事 + 图

### 2. IL-Property-ML — github.com/linfuxing123/IL-Property-ML
离子液体性质机器学习（密度/粘度/电导率/熔点——11,063 条/1,589 IL）

## 三、Zenodo DOI（数据/代码归档）
- 10.5281/zenodo.21898949（IL-Property-ML v1.0）
- 10.5281/zenodo.21960800（IL-MLIP-Benchmark v1.5.0）
- 10.5281/zenodo.21941824（Digital Discovery 姊妹）
- 10.5281/zenodo.21931665（逆向设计 predictors）
- 10.5281/zenodo.21996950 / 21997263（CES 补充）
- 10.5281/zenodo.22012503（等变创新点）

## 四、核心成果（统一律）
**等变替代统一标度律**：L = L∞ + A_s·N^(-α(s)) + B_s·D^(-β_eff(C; s, κ))
- β_eff：32ch 0.02 → 64ch 1.19 → 128ch 1.31（Pyr14-FSI）
- **临界容量 C* ≈ 52.6 通道**（β_max=1.313，σ_w≈9%）
- 对称性折扣 κ_eff = κ/s^m

## 五、投稿论文（7 篇 + 数据集）
1. JCED je-2026-00474q（IL 性质预测）
2. Chemical Engineering Science（数据增强/标度律）
3. Molecular Informatics 7514015（导率/热力学）
4. ACS Sust Chem Eng sc-2026-09624s（GNN vs 描述符）
5. JCIM ci-2026-027782（逆向设计）
6. JPC B jp-2026-056503（IL 导电性）
7. Digital Discovery DD-ART-08-2026-000620（预测器分歧）
8. IL-MLIP-Benchmark → JCTC（数据集，在审）
9. Equivariance as a Substitutable Resource → JCTC（在审）
10. Quantitative Laws of Equivariance Substitutability（统一律——投稿就绪）
