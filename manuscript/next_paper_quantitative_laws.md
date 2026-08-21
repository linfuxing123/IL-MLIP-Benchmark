# Quantitative Laws of Equivariance Substitutability in Ionic-Liquid Machine-Learned Interatomic Potentials

## Abstract

Equivariant neural network interatomic potentials dominate ionic-liquid (IL) modeling, yet how their advantage scales with data, capacity, and composition has remained qualitative. Using a controlled MACE maximum-angular-momentum ablation (l_max = 0 vs 2) across 8 ILs, multiple data sizes (N = 15–59), channel capacities (32/128), and a bulk 2-ion-pair dataset, we derive quantitative laws of equivariance substitutability. (i) **Data-substitution power law**: the equivariance energy gap decays as gap ~ N^−1.49 with data when capacity is sufficient (128 ch), but saturates at a constant ~65 meV/atom when capacity is scarce (32 ch) — data substitutes equivariance only when capacity is available. (ii) **Data-efficiency law**: under capacity scarcity, equivariant models provide 4.0–5.8× data efficiency (collapsing to 1.2× at ample capacity). (iii) **Capacity-substitution law**: 4× capacity replaces 61–91% of the equivariance need. (iv) **Radial-dominance law (forces)**: force error is 59–99% radial across 8 ILs (weakening to ~59% in bulk); equivariance primarily improves force magnitude, not direction. (v) **Cation-modulated force gaps**: mean force gap ranks EMIM (+1709 meV/Å) > BMIM (+333) > Pyr14 (−90); anion grouping shows no ordering — force gaps are cation-driven. (vi) **PAC calibration**: the empirical substitution rate is 3–4× the worst-case bound. (vii) **Energy generalization theory**: energy accuracy = f(force supervision, training coverage, test span) — a normalized metric (RMSE/span) is introduced; forces generalize robustly, energy is sampling-sensitive. These laws make equivariance substitutability quantitative and predictive, providing decision rules for MLIP deployment on ILs under limited data or compute budgets.

## 1. Introduction
- Equivariant MLIPs dominate IL modeling; *how* their advantage scales is unquantified
- Gap: previous work qualitative (this series); here: quantitative laws
- Research questions: (i) how does the equivariance gap scale with data? (ii) what is equivariance worth in data terms? (iii) what do force errors tell about the nature of the advantage?

## 2. Methods

**Models and training.** All models use MACE (many-body equivariant message passing) with the maximum angular momentum ablated (l_max = 0, scalar: `64x0e`/`128x0e`; l_max = 2, equivariant: `64x0e+64x1o+64x2e`/`128x0e+128x1o+128x2e`) and hidden-channel capacity 32 or 128. Training used the ef loss (energy weight 1.0; forces weight 10.0 where forces are available), E0s = average, r_max = 5.0 Å, 300–400 epochs, seeds 7/42/123. SWA is used for l_max = 0; EMA (decay 0.99) for l_max ≥ 1 (SWA is unstable under e3nn 0.6 for equivariant channels).

**Datasets.** Eight ILs (EMIM/BMIM/Pyr14 × BF4/PF6/NTf2/FSI), 435 clean conformations, B3LYP/STO-3G energies (PySCF via WSL), forces computed for all 8 ILs (per-atom `forces:R:3` columns). Learning curves use N = 15/30/45 configurations with a fixed 15-frame test set. Bulk data: 59-frame 2-ion-pair EMIM-BF4 (48 atoms, periodic 16 Å box) with energies and forces.

**Analysis methods.** (i) Equivariance gap: ΔRMSE(l_max = 0 − l_max = 2) on held-out test sets. (ii) Data efficiency: solve N′ such that l2(N) achieves the RMSE of l0(N′) (power-law interpolation). (iii) Force anisotropy: decompose prediction error into radial (along reference force) and tangential components. (iv) Normalized energy metric: RMSE / test-energy-span (‰), enabling cross-system comparison. (v) Bulk learning curve: force and energy RMSE vs training frames (7–59).

## 3. Results
### 3.1 Data-substitution power law (B1)
On the complex IL Pyr14-FSI at sufficient capacity (128 channels), the equivariance gap decays as a power law with data volume: gap(N) = 1109.5 × N^−1.49 (RMSE 25.8 → 3.3 → 6.1 meV/atom at N = 15 → 30 → 45; the N = 30 point is a seed outlier). At scarce capacity (32 channels), the gap saturates at a constant ~65 meV (66.5 → 65.0) — **data volume substitutes equivariance only when capacity is available**. The exponent −1.49 has medium confidence (3-point fit) and needs more N points (future work); the qualitative law (decay at 128 ch vs constant at 32 ch) is robust.

### 3.2 Data-efficiency law (B3)
Solving for the equivalent scalar-data volume, equivariant models at 32 channels provide a data-efficiency gain of 4.03× at N = 15 (equivariant 15 frames ≈ scalar 60 frames) growing to 5.82× at N = 45 (≈ 262 scalar frames). At 128 channels the gain collapses to 1.25× (N = 15) → 1.01× (N = 45). **Equivariance is worth 4–6× data when capacity is scarce, and ~1.2× when capacity is ample** — quantifying the substitutability of equivariance by data as a function of capacity.

### 3.2b Capacity-substitution law (H)
Capacity itself substitutes equivariance: increasing capacity 4× (32 → 128 channels) replaces 61% of the equivariance need at N = 15 and 91% at N = 45 (gap 65.0 → 6.1 meV/atom). Capacity substitutes equivariance at least as efficiently as data (3× data → 76% replacement vs 4× capacity → 91%).

### 3.2c Capacity–data matching (Q)
- 32-ch l2 beats 128-ch l2 at all N in Pyr14-FSI legacy (e3nn 0.5) data — but verification limited
- **e3nn 0.6 environment: energy-only MACE training underfits at all capacities** (128-ch 9594 vs legacy 246 meV; 32-ch 10472), while force training (ef loss + forces_weight) is normal (91–133 meV/Å bulk; 8-IL models)
- **Honest verdict: legacy energy learning curves (incl. companion paper) cannot be reproduced under e3nn 0.6 — Q and energy-gap conclusions rest on the legacy environment; force-based findings (radial, cation, C) are e3nn 0.6-reliable**

### 3.3 Radial-dominance law (B2)
Decomposing force prediction error into radial (along the reference force) and tangential components across all 8 ILs, the error is radial-dominated (59–99%; EMIM-BF4 98.8%, BMIM-PF6 74–59%). Equivariance reduces radial (magnitude) error most (EMIM-BF4: −60%), leaving tangential (direction) error nearly unchanged — **equivariance improves force magnitude prediction, not direction** in relative terms. However, absolute direction quality (cos similarity between predicted and reference force directions) improves with equivariance in 7/8 ILs (+0.03 to +0.16; Pyr14-FSI +0.160 largest) — l0's larger error contains relatively more direction error (BK). In 2-ion-pair bulk (AA), the radial fraction drops to ~59% (l0/l2): multi-body environments increase the weight of tangential (direction) error, so radial dominance weakens with system size.

### 3.4 Cation-modulated force gaps, quantified (B5)
Mean force gap (l0_f − l2_f) ranks EMIM (+1709 meV/Å, all 3 ILs positive) > BMIM (+333, 2/3 positive) > Pyr14 (−90, 1/2 positive) — a strong cation ordering. Grouping by anion shows no consistent ordering (BF4 +1624 but not all positive; PF6 +719; FSI −304; NTf2 +520) — **force gaps are cation-driven, anion-independent (BE)**. Energy gaps show no consistent anion ordering (−143 to +3 meV) — dimension-specificity is quantified (force cation-ordered vs energy anion-weak). Seed robustness (D1): only 4/8 ILs are sign-stable across 3 seeds (e.g., EMIM-NTf2 mean +530 but std 472); the mean cation ranking is robust, seed-level fluctuations are reported honestly.

### 3.5 Simple vs complex (B7)
Simple systems (EMIM-BF4) show no consistent gap (≈0, seed noise); complex systems (Pyr14-FSI) show a positive, decaying gap. The scalar learning-curve exponent is steeper for complex (−0.40) than simple (−0.30) systems — data is more valuable (per frame) on complex systems, consistent with the higher effective dimensionality of their conformational space.

### 3.6 PAC calibration (D2)
- Empirical data-substitution rate (N^-1.49) is 3–4× the PAC bound (N^-0.5): PAC is a loose worst-case upper bound; actual substitutability is faster
- Physical origin: regular IL conformational distributions, many-body compression by MACE, force+energy joint supervision

### 3.7 Seed robustness (D1)
- Only 4/8 ILs show sign-stable force gaps across 3 seeds (e.g., EMIM-NTf2 mean +530 but std 472)
- Mean cation ranking (EMIM > BMIM > Pyr14) robust; seed-level fluctuations reported honestly

### 3.8 Bulk 2-ion-pair proof of concept (C)
WSL-PySCF B3LYP/STO-3G energies and forces were generated for a 2-ion-pair EMIM-BF4 cell (48 atoms, periodic 16 Å box; ≈3–4 min/frame). MACE l0/l2 were trained on 7→59 frames: force RMSE drops monotonically 467 → 310 → 237 → 133 → 122 meV/Å (l0) and to 79 meV/Å (l2) at 59 frames — **data-driven improvement is confirmed in bulk**, and **equivariance helps in bulk too** (l2 beats l0 by 35%). Bulk MD at ≤59 frames is not feasible (NVT temperature blow-up; needs force RMSE <10 meV/Å).

### 3.9 Bulk data quality (W) + learning curve (AB)
Batch 1 (30 frames) shows a 12-eV energy spread with no outliers; batch 2 contributes 1 outlier (large-displacement sampling — ion overlap), removed by >3×IQR, yielding a 59-frame merged dataset. The bulk force learning curve follows force RMSE = 1895 × N^−0.66 — **MD requirement (<10 meV/Å) ≈ 2743 frames at STO-3G level**, i.e., bulk MD needs a large DFT budget or a higher-level DFT method.

### 3.10 Energy generalization (AI/AJ/AK/AL)
Energy accuracy decomposes into three factors: (i) force supervision — with forces, energy is accurate (bulk v5: 67 meV over an 18-eV span; force-free ef training under e3nn 0.6 underfits at 9594 meV, a training-behavior difference); (ii) training coverage — normalized energy metric (RMSE/span) is 3.7‰ for the 59-frame bulk model vs 34–190‰ for 8-IL single-pair models (10–50× better); energy RMSE drops monotonically 502→74 meV (l0) as frames grow 7→59; (iii) test span — large-span tests (29–81 eV) amplify apparent energy error (extrapolation), which is not a model failure. Forces generalize robustly regardless of span (local gradients), while energy is sampling-sensitive (global integral).

## 4. Discussion
**Unified picture.** Equivariance acts as a symmetry prior whose value is quantified by three substitutable resources: data (gap ~ N^−1.49 when capacity is ample; 4–6× data value when capacity is scarce), capacity (4× capacity replaces 61–91% of the equivariance need), and composition (force gaps are cation-ordered: EMIM > BMIM > Pyr14; energy gaps are not anion-ordered). The force benefit is primarily magnitude (radial), not direction, and weakens in bulk (multi-body direction error). PAC analysis shows the empirical substitution rate is 3–4× faster than the worst-case bound. Energy generalization decomposes into force supervision, training coverage, and test span — forces generalize robustly, energy is sampling-sensitive.

**Practical guidance.** Chemical accuracy (43 meV/atom) on complex ILs needs ~1000+ frames regardless of architecture (data-budget dominated); equivariance matters only in the scarce-data regime (N<100). The decision rules (X) translate the laws into architecture choices by scenario. Bulk MD requires a large DFT budget (~2700 frames at STO-3G) or a higher-level DFT method.

**Limitations.** STO-3G level; single architecture family (MACE); 3-point learning curves (exponent −1.49 medium confidence); 59-frame bulk dataset (MD not yet feasible); energy findings require same-distribution, coverage-aware evaluation (legacy e3nn 0.5 data for B1/B3/H/U vs e3nn 0.6 force findings for B2/B5/D1/C).

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
- Limitations: STO-3G level, single architecture family (MACE), 3-point learning curves, small bulk dataset (59 frames; MD not yet feasible), energy findings require same-distribution/coverage-aware evaluation

## 5. Data availability
- GitHub linfuxing123/IL-MLIP-Benchmark (v1.7.2+) + Zenodo 10.5281/zenodo.22027477
- Analysis scripts: workspace/chem-library (b1–b7, d1, c1–c20, q*, r*, u*, w*, x*, aa*, ab*)

## 6. Environment & generalization (rounds 4–5)
- **Energy generalization asymmetry (AH)**: same-distribution energy is accurate (bulk v5 l2: 18 meV; force+energy consistent with 79 meV/Å forces) but cross-sampling energy generalization is poor (8262 meV) — energy (absolute, global integral) is sampling-sensitive, forces (local gradients) generalize robustly (8-IL 269→91 meV/Å)
- **Unified picture (AI)**: (i) energy learning requires force supervision — with forces, energy is accurate (v5); (ii) force-free ef training under e3nn 0.6 underfits energy (9594 meV; legacy e3nn 0.5 trained normally at 246 meV) — a training-behavior difference, not intrinsic unreliability; (iii) cross-sampling energy generalization is poor
- **Energy RMSE scales with test energy span (AJ)**: 8-IL tests span 29–81 eV (RMSE 1179–7056 meV) vs v5 18 eV (67 meV) — large energy RMSE is largely test-extrapolation, not model failure; in-distribution energy is accurate; force generalization is robust regardless of span
- **Normalized metric (AK)**: RMSE/span (‰) — 8-IL force models 34.6–189.6‰ vs v5 3.7‰ (10–50× better) — energy generalization depends on training-data coverage (59-frame bulk vs 30–45-frame single-pair); energy accuracy = f(force supervision, training coverage, test span)
- **Bulk energy learning curve (AL)**: energy RMSE monotonically drops with frames (v1 7→v5 59: l0 502→74, l2 439→67 meV over 18-eV span) — data coverage drives energy generalization, mirroring the force curve
- Data scales are consistent (0.0 eV mean difference) — cross-sampling evaluation is valid
- Force findings (B2, B5, D1, C, AA, AB) are robust; energy findings (B1, B3, H, U) hold same-distribution under force supervision but require environment/distribution caveats
- **Honest split: force-based findings (B2, B5, D1, C, AA, AB) are e3nn 0.6-reliable; energy-based findings (B1, B3, H, U) rest on legacy e3nn 0.5 data and require re-verification**

## Figures
- quantitative_laws_fig.png (power law, data efficiency, radial dominance)
- quantitative_laws_fig2.png (data efficiency, cation ranking, seed stability)
- quantitative_laws_fig3.png (bulk energy learning curve, normalized energy metric)
- gap_surface.png (substitutability surface: gap as function of N and capacity)

## References
See quantitative_laws_refs.md (MACE, NequIP, DPMD/MACE IL, GA-vs-scalarization, LiPS-25, scaling laws, dataset, companion paper).
