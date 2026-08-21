# Quantitative Laws of Equivariance Substitutability in Ionic-Liquid Machine-Learned Interatomic Potentials

## 1. Introduction
- Equivariant MLIPs dominate IL modeling; *how* their advantage scales is unquantified
- Gap: previous work qualitative (this series); here: quantitative laws
- Research questions: (i) how does the equivariance gap scale with data? (ii) what is equivariance worth in data terms? (iii) what do force errors tell about the nature of the advantage?

## 2. Methods
- MACE l_max ablation (0 vs 2), 32/128 channels, seeds 7/42/123
- IL dataset: 8 ILs, 435 configurations (B3LYP/STO-3G) + forces
- Learning curves: N = 15/30/45 (Pyr14-FSI, EMIM-BF4)
- Force anisotropy: decompose prediction error into radial (along reference force) and tangential components

## 3. Results
### 3.1 Data-substitution power law (B1)
- gap = 1109.5 × N^-1.49 (128 ch, Pyr14-FSI); constant ~65 meV (32 ch)
- **Data volume substitutes equivariance only when capacity is sufficient**

### 3.2 Data-efficiency law (B3)
- 32 ch: equivariance = 4.03× data (N=15) → 5.82× (N=45); 128 ch: 1.25×
- **Equivariance value = data-efficiency gain, capacity-dependent**

### 3.2b Capacity-substitution law (H)
- 4× capacity (32→128 ch) replaces 61–91% of the equivariance need (N=45: 91%)
- Capacity substitutes equivariance at least as efficiently as data (3× data → 76% vs 4× capacity → 91%)

### 3.2c Capacity–data matching (Q)
- 32-ch l2 beats 128-ch l2 at all N in Pyr14-FSI legacy (e3nn 0.5) data — but verification limited
- **e3nn 0.6 environment: energy-only MACE training underfits at all capacities** (128-ch 9594 vs legacy 246 meV; 32-ch 10472), while force training (ef loss + forces_weight) is normal (91–133 meV/Å bulk; 8-IL models)
- **Honest verdict: legacy energy learning curves (incl. companion paper) cannot be reproduced under e3nn 0.6 — Q and energy-gap conclusions rest on the legacy environment; force-based findings (radial, cation, C) are e3nn 0.6-reliable**

### 3.3 Radial-dominance law (B2)
- Force error radial-dominated across all 8 ILs (59–99% radial; EMIM-BF4 98.8%, BMIM-PF6 74–59%)
- Equivariance cuts radial (magnitude) error most (EMIM-BF4: −60%), tangential (direction) less
- **Equivariance improves force magnitude primarily; direction error secondary, system-dependent**
- **Bulk caveat (AA)**: in 2-ion-pair bulk, radial fraction drops to ~59% (l0/l2) — multi-body environments increase tangential (direction) error weight; radial dominance weakens with system size

### 3.4 Cation-modulated force gaps, quantified (B5)
- Mean force gap: EMIM +1709 > BMIM +333 > Pyr14 −90 meV/Å (strong cation ordering)
- Energy gap shows no consistent anion ordering (−143 to +3 meV; weak) — dimension-specificity quantified
- Seed robustness: 4/8 ILs sign-stable across 3 seeds; mean ranking robust

### 3.5 Simple vs complex (B7)
- Simple (EMIM-BF4): gap ≈ 0 (noise); complex (Pyr14-FSI): positive + decaying
- Scalar learning exponent: complex −0.40 vs simple −0.30 (data more valuable on complex)

### 3.6 PAC calibration (D2)
- Empirical data-substitution rate (N^-1.49) is 3–4× the PAC bound (N^-0.5): PAC is a loose worst-case upper bound; actual substitutability is faster
- Physical origin: regular IL conformational distributions, many-body compression by MACE, force+energy joint supervision

### 3.7 Seed robustness (D1)
- Only 4/8 ILs show sign-stable force gaps across 3 seeds (e.g., EMIM-NTf2 mean +530 but std 472)
- Mean cation ranking (EMIM > BMIM > Pyr14) robust; seed-level fluctuations reported honestly

### 3.8 Bulk 2-ion-pair proof of concept (C)
- WSL-PySCF B3LYP/STO-3G energies+forces for 2-ion-pair EMIM-BF4 (48 atoms); 30 frames generated (≈3–4 min/frame)
- MACE l0/l2 trained: force RMSE 342 (7 frames) → 269 (30) → 133 (l0, 41) / 91 meV/Å (l2, 41) — data-driven improvement path confirmed
- **Equivariance helps in bulk too**: l2 beats l0 by 32% at 41 frames (91 vs 133 meV/Å) — consistent with isolated-ion-pair finding
- Bulk MD not yet feasible at 41 frames (NVT temperature blow-up — needs ~100–200 frames; force RMSE <10 meV/Å); honest limitation
- Bulk (multi-ion-pair) data generation → training path established; 41-frame merged dataset (outlier-filtered)

### 3.9 Bulk data quality (W)
- Batch 1 (30 frames): energy spread 12 eV, no outliers — good sampling
- Batch 2: 1 outlier (large-displacement sampling — ion overlap) — filtered by >3×IQR
- Merged 41-frame dataset (bulk_emim_bf4_all.xyz) for v4 retraining

## 4. Discussion
- Unified picture: equivariance = symmetry prior worth 4–6× data when capacity-scarce, ~1.2× when capacity-free; force benefit = magnitude (radial), system-dependent
- Practical guidance: chemical accuracy (43 meV/atom) on complex ILs needs ~1000+ frames regardless of architecture (data-budget dominated); equivariance matters only in the scarce-data regime (N<100)

### Decision rules (X)
| Scenario | Recommended |
|---|---|
| Scarce data (N<100), complex IL, small capacity | equivariant l2 (4–6× data value) |
| Scarce data, simple IL (BF4) | scalar l0 (equivariance redundant) |
| Large data (N>500) | scalar l0 + data (chemical accuracy, architecture-independent) |
| Force prediction, EMIM cation | equivariant l2 (force gap +1709 meV/Å) |
| Force prediction, Pyr14 cation | scalar l0 (force gap −90) |
- Power-law exponent −1.49 has medium confidence (3-point fit; N=30 outlier) — more N points needed (future work)
- 128-ch overfitting caveat: Q verification limited by e3nn-version incompatibility of legacy models; EMIM 32-ch underfits (system-specific, not training parameter)
- Practical guidance: scalar MACE + data for simple ILs; equivariant for complex/scarce-data
- Limitations: STO-3G level, single architecture family (MACE), 3-point learning curves, small bulk dataset (7 frames concept validation)

## 5. Data availability
- GitHub linfuxing123/IL-MLIP-Benchmark (v1.7.2+) + Zenodo 10.5281/zenodo.22027477
- Analysis scripts: workspace/chem-library (b1–b7, d1)

## Figures
- quantitative_laws_fig.png (power law, data efficiency, radial dominance)
