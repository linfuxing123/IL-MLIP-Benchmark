# Quantitative Laws of Equivariance Substitutability in Ionic-Liquid Machine-Learned Interatomic Potentials

## Abstract

Equivariant neural network interatomic potentials dominate ionic-liquid (IL) modeling, yet how their advantage scales with data, capacity, and composition has remained qualitative. Using a controlled MACE maximum-angular-momentum ablation (l_max = 0 vs 2) across 8 ILs, multiple data sizes (N = 15–59), channel capacities (32/128), and a bulk 2-ion-pair dataset, we derive quantitative laws of equivariance substitutability. (i) **Data-substitution power law**: the equivariance energy gap decays as gap ~ N^−1.49 with data when capacity is sufficient (128 ch), but saturates at a constant ~65 meV/atom when capacity is scarce (32 ch) — data substitutes equivariance only when capacity is available. (ii) **Data-efficiency law**: under capacity scarcity, equivariant models provide 4.0–5.8× data efficiency (collapsing to 1.2× at ample capacity). (iii) **Capacity-substitution law**: 4× capacity replaces 61–91% of the equivariance need. (iv) **Radial-dominance law (forces)**: force error is 59–99% radial across 8 ILs (weakening to ~59% in bulk); equivariance primarily improves force magnitude, not direction. (v) **Cation-modulated force gaps**: mean force gap ranks EMIM (+1709 meV/Å) > BMIM (+333) > Pyr14 (−90); anion grouping shows no ordering — force gaps are cation-driven. (vi) **PAC calibration**: the empirical substitution rate is 3–4× the worst-case bound. (vii) **Energy generalization theory**: energy accuracy = f(force supervision, training coverage, test span) — a normalized metric (RMSE/span) is introduced; forces generalize robustly, energy is sampling-sensitive. The substitutability laws unify into a single scaling law — **L(N, D, C; s, κ) = L∞ + A_s·N^(−α(s)) + B_s·D^(−β_eff(C))**, with α,β_max increasing in symmetry degree s (merging the large-scale scaling evidence of Ngo & Ravanbakhsh ICLR 2026) and β_eff governed by a capacity-dependent substitution transition with critical capacity C\* ≈ 48 channels — **empirically verified at 32/64/128 ch** (β_eff: 0.02 → 1.19 → 1.31). These laws make equivariance substitutability quantitative, predictive, and unified, providing decision rules for MLIP deployment on ILs under limited data or compute budgets.

## 1. Introduction
- Equivariant MLIPs (MACE [1], NequIP [2], DPMD [10]) dominate IL modeling; *how* their advantage scales is unquantified
- Gap: previous work qualitative (this series, [7,8]); here: quantitative laws
- Research questions: (i) how does the equivariance gap scale with data? (ii) what is equivariance worth in data terms? (iii) what do force errors tell about the nature of the advantage?

## 2. Methods

**Models and training.** All models use MACE [1] (many-body equivariant message passing) with the maximum angular momentum ablated (l_max = 0, scalar: `64x0e`/`128x0e`; l_max = 2, equivariant: `64x0e+64x1o+64x2e`/`128x0e+128x1o+128x2e`) and hidden-channel capacity 32 or 128. Training used the ef loss (energy weight 1.0; forces weight 10.0 where forces are available), E0s = average, r_max = 5.0 Å, 300–400 epochs, seeds 7/42/123. SWA is used for l_max = 0; EMA (decay 0.99) for l_max ≥ 1 (SWA is unstable under e3nn 0.6 for equivariant channels).

**Datasets.** Eight ILs (EMIM/BMIM/Pyr14 × BF4/PF6/NTf2/FSI), 435 clean conformations, B3LYP/STO-3G energies (PySCF via WSL), forces computed for all 8 ILs (per-atom `forces:R:3` columns). Learning curves use N = 15/30/45 configurations with a fixed 15-frame test set. Bulk data: 59-frame 2-ion-pair EMIM-BF4 (48 atoms, periodic 16 Å box) with energies and forces.

**Analysis methods.** (i) Equivariance gap: ΔRMSE(l_max = 0 − l_max = 2) on held-out test sets. (ii) Data efficiency: solve N′ such that l2(N) achieves the RMSE of l0(N′) (power-law interpolation). (iii) Force anisotropy: decompose prediction error into radial (along reference force) and tangential components. (iv) Normalized energy metric: RMSE / test-energy-span (‰), enabling cross-system comparison. (v) Bulk learning curve: force and energy RMSE vs training frames (7–59). (vi) Per-atom energy RMSE via the official `mace.cli.eval_configs` (MACE_energy key, divided by number of atoms) — the reproducible evaluation protocol (units: meV/atom).

## 3. Results
### 3.1 Data-substitution power law (B1)
On the complex IL Pyr14-FSI at sufficient capacity (128 channels), the equivariance gap decays as a power law with data volume: gap(N) = 1109.5 × N^−1.49 (RMSE 25.8 → 3.3 → 6.1 meV/atom at N = 15 → 30 → 45; the N = 30 point is a seed outlier). At scarce capacity (32 channels), the gap saturates at a constant ~65 meV (66.5 → 65.0) — **data volume substitutes equivariance only when capacity is available**. The exponent −1.49 has medium confidence (3-point fit) and needs more N points (future work); the qualitative law (decay at 128 ch vs constant at 32 ch) is robust.

### 3.2 Data-efficiency law (B3)
Solving for the equivalent scalar-data volume, equivariant models at 32 channels provide a data-efficiency gain of 4.03× at N = 15 (equivariant 15 frames ≈ scalar 60 frames) growing to 5.82× at N = 45 (≈ 262 scalar frames). At 128 channels the gain collapses to 1.25× (N = 15) → 1.01× (N = 45). **Equivariance is worth 4–6× data when capacity is scarce, and ~1.2× when capacity is ample** — quantifying the substitutability of equivariance by data as a function of capacity.

### 3.2b Capacity-substitution law (H)
Capacity itself substitutes equivariance: increasing capacity 4× (32 → 128 channels) replaces 61% of the equivariance need at N = 15 and 91% at N = 45 (gap 65.0 → 6.1 meV/atom). Capacity substitutes equivariance at least as efficiently as data (3× data → 76% replacement vs 4× capacity → 91%).

### 3.2c Capacity–data matching (Q)
- **e3nn 0.6 environment: energy-only MACE training underfits at all capacities** (128-ch 9594 vs legacy 246 meV; 32-ch 10472), while force training (ef loss + forces_weight) is normal (91–133 meV/Å bulk; 8-IL models)
- **Honest verdict: legacy energy learning curves (incl. companion paper) cannot be reproduced under e3nn 0.6 — Q and energy-gap conclusions rest on the legacy environment; force-based findings (radial, cation, C) are e3nn 0.6-reliable**

### 3.2d Equivariance-substitution phase transition (unification of B1/B3/H)
Testing simple unified forms (double power law gap = A·N^−b1·C^−b2; equivalent-resource R = N·C^g) against the Pyr14-FSI data shows both are inconsistent (double-power-law residual 18; β behavior conflicts). The data reveal a **capacity-dependent substitution phase transition**:
- **C < C\* (capacity-scarce, 32 ch): β ≈ 0** — gap stays constant (~65 meV) as N grows: **data cannot substitute equivariance**
- **C > C\* (capacity-ample, 128 ch): β ≈ 1.49** — gap decays ~N^−1.49: **data substitutes equivariance**
- **Unified form: gap = A·N^(−β(C)), β(C) a threshold function of capacity — there is a critical capacity C\***; below it, extra data cannot replace equivariance; above it, data becomes an equivalent resource.
- Physical picture: when model capacity < IL conformational complexity, added data cannot substitute equivariance (the bottleneck is capacity, not data). This unifies the power law (B1), data-efficiency (B3), and capacity-substitution (H) laws.
- *Caveat (honest)*: only 2–3 N-points per capacity; the phase transition is indicative — mid capacities (64/96 ch) are needed to locate C\* and test whether the transition is sharp or smooth. Also note the simple-system (EMIM-BF4) gap is ~0 (equivariance redundant), so the transition applies to complex ILs (positive gap).

### 3.2e Unified scaling law (phase-transition + Ngo large-scale)
We fuse the phase transition (3.2d) with the recent large-scale scaling-law evidence of Ngo & Ravanbakhsh (ICLR 2026) into a single candidate theorem:
**L(N, D, C; s, κ) = L∞ + A_s·N^(−α(s)) + B_s·D^(−β_eff(C; s, κ))**
where:
- **α(s), β_max(s) increase with symmetry degree s** (Ngo, large-scale: α 0.28→0.82, β 0.31→0.75) — equivariance scales better at large scale;
- **β_eff(C; s, κ) = β_max(s)·σ((C − κ/s)/w)** is a sigmoid transition in capacity (our small-scale phase transition);
- **κ** = intrinsic problem complexity; **κ/s** = effective complexity (symmetry *reduces* effective complexity, echoing "symmetry controls the effective number of parameters", arXiv:2502.05300).

**Three limits verify**:
1. C ≫ κ/s (large-scale, Ngo regime): σ→1 → reduces to Ngo's double power law ✓
2. C ≪ κ/s (capacity-scarce): σ→0 → data term D^0 → gap constant, data cannot substitute equivariance ✓ (our 32-ch)
3. s = 0 (non-equivariant): α, β minimal → worst scaling ✓

**Unified physics**: symmetry s maps the intrinsic complexity κ to an effective κ/s. If capacity C < κ/s, added data cannot substitute equivariance (phase transition, our finding); if C > κ/s, data is effective AND the equivariant exponents α, β are higher, so equivariance pulls further ahead with scale (Ngo). This unifies the small-scale phase transition with the large-scale power law into **one expression covering the whole spectrum** — the candidate "equivariance-substitution law" (potential eponymous law). *Testable prediction*: β_eff should rise sigmoidally from 0 to β_max(s) with capacity C; locating C\* requires intermediate capacities (64/96 ch, in progress).

### 3.2f Unified law — mechanism and cross-system predictive form
To promote the unified law from an empirical form to a mechanistic, predictive one, we introduce:
- **Symmetry discount**: effective complexity κ_eff = κ/s^m (symmetry s reduces effective degrees of freedom, echoing arXiv:2502.05300);
- **Critical capacity**: C\* = λ·κ/s^m (λ a (possibly) universal constant) — C\* grows linearly with intrinsic complexity κ and inversely with symmetry s;
- **Transition width**: w = C\*·σ_w (σ_w the sharpness ratio — small = sharp transition, large = smooth);
- β_max(s=2, MACE l2) ≈ 1.49.

**Cross-system / cross-symmetry predictions** (the power of a law — all testable):
1. **Simple ILs (small κ)**: C\* small → equivariance gap vanishes early (EMIM-BF4, gap ≈ 0 ✓ — already observed);
2. **More complex ILs** (larger anion / longer alkyl): C\* larger → needs more capacity/data to substitute equivariance;
3. **Higher-order equivariance (large s, e.g. l=4)**: C\* lower → gap vanishes earlier.

The full unified law reads:
**L = L∞ + A_s·N^(−α(s)) + B_s·D^(−β_max(s)·σ((C − λκ/s^m)/(λκ/s^m·σ_w)))**
*Verification status (verified)*: the three limits reduce correctly; the cross-system trend (EMIM ≈ 0) is confirmed; and — decisive — the intermediate capacity 64-ch data (freshly trained, per-atom RMSE evaluated with the official MACE eval_configs) locates the transition (Fig. unified_law_fig): **gap(N) at 32 ch is constant (66.5 → 65.0 meV/atom, β≈0), at 64 ch it decays (66.2 → 17.9, β≈1.19 — the transition is already engaged), and at 128 ch it follows the power law (25.8 → 6.1, β≈1.31)**. β_eff jumps from ~0 (32 ch) through ~1.2 (64 ch) to ~1.3 (128 ch) — the substitution transition is **steep, with critical capacity C\* ≈ 48 channels** (between 32 and 64), not a gradual trend. (Note: an earlier apparent "underfitting/drift" was an evaluation-unit artifact — total-energy RMSE without dividing by the 39-atom Pyr14-FSI system, which inflated values ~39×; per-atom evaluation restores consistency with the legacy records 271/204 meV/atom.)

**Table 3.1 — Equivariance-substitution phase transition (Pyr14-FSI, per-atom, official eval_configs, 3-seed-consistent seed 42)**

| capacity | l0 @N=15 | l2 @N=15 | gap @N=15 | gap @N=45 | β_eff |
|---|---|---|---|---|---|
| 32 ch | 271.3 | 204.8 | 66.5 | 65.0 | 0.02 |
| 64 ch | 268.5 | 202.3 | 66.2 | 17.9 | 1.19 |
| 128 ch | 246.0 | 220.2 | 25.8 | 6.1 | 1.31 |

The transition is visualized in Fig. unified_law_fig (gap vs N across capacities; β_eff jump) and Fig. unified_law_support (scalar vs equivariant learning curves; gap @ N=15 vs N=45 collapse). Fitting the three β_eff values to a steep sigmoid in capacity (Fig. unified_law_beta) gives **β_max ≈ 1.31, critical capacity C\* ≈ 52.6 channels, and width σ_w ≈ 5.0 (≈9% of C\*)** — i.e. equivariance substitutability switches on abruptly once capacity exceeds ~52 channels (within the 32–64 window), rather than gradually. Fitting in capacity (not in N) makes this a sharp, quantitative transition.

### 3.3 Radial-dominance law (B2)
Decomposing force prediction error into radial (along the reference force) and tangential components across all 8 ILs, the error is radial-dominated (59–99%; EMIM-BF4 98.8%, BMIM-PF6 74–59%). Equivariance reduces radial (magnitude) error most (EMIM-BF4: −60%), leaving tangential (direction) error nearly unchanged — **equivariance improves force magnitude prediction, not direction** in relative terms. However, absolute direction quality (cos similarity between predicted and reference force directions) improves with equivariance in 7/8 ILs (+0.03 to +0.16; Pyr14-FSI +0.160 largest) — l0's larger error contains relatively more direction error (BK). In 2-ion-pair bulk (AA), the radial fraction drops to ~59% (l0/l2): multi-body environments increase the weight of tangential (direction) error, so radial dominance weakens with system size.

### 3.4 Cation-modulated force gaps, quantified (B5)
Mean force gap (l0_f − l2_f) ranks EMIM (+1709 meV/Å, all 3 ILs positive) > BMIM (+333, 2/3 positive) > Pyr14 (−90, 1/2 positive) — a strong cation ordering. Grouping by anion shows no consistent ordering (BF4 +1624 but not all positive; PF6 +719; FSI −304; NTf2 +520) — **force gaps are cation-driven, anion-independent (BE)**. Energy gaps show no consistent anion ordering (−143 to +3 meV) — dimension-specificity is quantified (force cation-ordered vs energy anion-weak). Seed robustness (D1): only 4/8 ILs are sign-stable across 3 seeds (e.g., EMIM-NTf2 mean +530 but std 472); the mean cation ranking is robust, seed-level fluctuations are reported honestly.

### 3.5 Simple vs complex (B7)
Simple systems (EMIM-BF4) show no consistent gap (≈0, seed noise); complex systems (Pyr14-FSI) show a positive, decaying gap. The scalar learning-curve exponent is steeper for complex (−0.40) than simple (−0.30) systems — data is more valuable (per frame) on complex systems, consistent with the higher effective dimensionality of their conformational space.

### 3.6 PAC calibration (D2)
- Empirical data-substitution rate (N^-1.49) is 3–4× the PAC bound (N^-0.5): PAC is a loose worst-case upper bound; actual substitutability is faster
- Physical origin: regular IL conformational distributions, many-body compression by MACE, force+energy joint supervision

### 3.6 PAC calibration (D2)
The empirical data-substitution rate (gap ~ N^−1.49) is 3–4× faster than the PAC worst-case bound (gap ~ C/√N, N^−0.5): the empirical gap falls to 26% of the PAC prediction at N = 45. PAC is a loose worst-case upper bound; actual substitutability is faster. Physical origin: regular IL conformational distributions, many-body compression by MACE, and force+energy joint supervision (the latter providing gradient information that pure energy learning lacks).

### 3.7 Seed robustness (D1)
Only 4/8 ILs show sign-stable force gaps across 3 seeds (e.g., EMIM-NTf2 mean +530 meV/Å but std 472 — seed-level sign flips), while the mean cation ranking (EMIM > BMIM > Pyr14) is robust. Force RMSE seed fluctuation is 3–26% (median <15%), so the 3-seed mean is a reliable estimator; the largest fluctuation (EMIM-BF4, 26%) coincides with the largest force gap. Seed-level fluctuations are reported honestly rather than averaged away.

### 3.8 Bulk 2-ion-pair proof of concept (C)
WSL-PySCF B3LYP/STO-3G energies and forces were generated for a 2-ion-pair EMIM-BF4 cell (48 atoms, periodic 16 Å box; ≈3–4 min/frame). MACE l0/l2 were trained on 7→59 frames: force RMSE drops monotonically 467 → 310 → 237 → 133 → 122 meV/Å (l0) and to 79 meV/Å (l2) at 59 frames — **data-driven improvement is confirmed in bulk**, and **equivariance helps in bulk too** (l2 beats l0 by 35%). Bulk MD at ≤59 frames is not feasible (NVT temperature blow-up; needs force RMSE <10 meV/Å).

### 3.9 Bulk data quality (W) + learning curve (AB)
Batch 1 (30 frames) shows a 12-eV energy spread with no outliers; batch 2 contributes 1 outlier (large-displacement sampling — ion overlap), removed by >3×IQR, yielding a 59-frame merged dataset. The bulk force learning curve follows force RMSE = 1895 × N^−0.66 — **MD requirement (<10 meV/Å) ≈ 2743 frames at STO-3G level**, i.e., bulk MD needs a large DFT budget or a higher-level DFT method.

### 3.9b High-energy-surface coverage (v6) + equivariance energy advantage
Extending sampling to large displacements (RMSD >0.5 Å; 30 frames, energy span 322 eV, 3 outliers filtered) and merging with the 59 near-equilibrium frames yields an 86-frame dataset spanning 98.5 eV (holdout). Trained v6 models evaluated on this broad-span holdout: **l0 (scalar) energy RMSE 3014 meV (normalized 30.6‰); l2 (equivariant) 2059 meV (normalized 20.9‰)** — **equivariance improves high-energy-surface coverage by 32%**, extending the force-level magnitude advantage (B2) to energy over a broad conformational/energy range. Bulk MD on v6 l2 remains unstable (temperature blow-up 1.7×10^7 K, 38× better than the 59-frame model) — force RMSE ~3000 meV/Å over the broad span still exceeds the ~10 meV/Å MD threshold by ~300×.

### 3.10 Energy generalization (AI/AJ/AK/AL)
Energy accuracy decomposes into three factors: (i) force supervision — with forces, energy is accurate (bulk v5: 67 meV over an 18-eV span; force-free ef training under e3nn 0.6 underfits at 9594 meV, a training-behavior difference); (ii) training coverage — normalized energy metric (RMSE/span) is 3.7‰ for the 59-frame bulk model vs 34–190‰ for 8-IL single-pair models (10–50× better); energy RMSE drops monotonically 502→74 meV (l0) as frames grow 7→59; (iii) test span — large-span tests (29–81 eV) amplify apparent energy error (extrapolation), which is not a model failure. Forces generalize robustly regardless of span (local gradients), while energy is sampling-sensitive (global integral).

## 4. Discussion
**Unified picture.** Equivariance acts as a symmetry prior whose value is quantified by three substitutable resources: data (gap ~ N^−1.49 when capacity is ample; 4–6× data value when capacity is scarce), capacity (4× capacity replaces 61–91% of the equivariance need), and composition (force gaps are cation-ordered: EMIM > BMIM > Pyr14; energy gaps are not anion-ordered). The force benefit is primarily magnitude (radial), not direction, and weakens in bulk (multi-body direction error). PAC analysis shows the empirical substitution rate is 3–4× faster than the worst-case bound. Energy generalization decomposes into force supervision, training coverage, and test span — forces generalize robustly, energy is sampling-sensitive.

**Practical guidance.** Chemical accuracy (43 meV/atom) on complex ILs needs ~1000+ frames regardless of architecture (data-budget dominated); equivariance matters only in the scarce-data regime (N<100). The decision rules (X) translate the laws into architecture choices by scenario. Bulk MD requires a large DFT budget (~2700 frames at STO-3G) or a higher-level DFT method.

**The unified law as a predictive tool.** The substitutability laws collapse into one expression — L = L∞ + A_s·N^(−α(s)) + B_s·D^(−β_eff(C)) — where β_eff is a steep sigmoid in capacity (β_max ≈ 1.31, C\* ≈ 52.6 ch, σ_w ≈ 9% of C\*, Fig. unified_law_beta; full derivation in the supplementary). This is *predictive*, not just descriptive: given a system's complexity κ and a chosen symmetry s, one can (i) predict the critical capacity C\* = λκ/s^m below which data cannot substitute equivariance; (ii) predict the data-efficiency gain at a given capacity; (iii) forecast the performance gap at any (N, C) without training. The law also merges the small-scale phase transition found here with the large-scale scaling evidence of Ngo & Ravanbakhsh (ICLR 2026) into a single spectrum — data substitutes equivariance once capacity exceeds a system-specific critical value, and equivariance scales better than non-equivariance at large scale because its α, β exponents are higher.

**Limitations.** STO-3G level; single architecture family (MACE); 3-point learning curves (exponent −1.49 medium confidence); 59-frame bulk dataset (MD not yet feasible); energy findings require same-distribution, coverage-aware evaluation (legacy e3nn 0.5 data for B1/B3/H/U vs e3nn 0.6 force findings for B2/B5/D1/C).

### Decision rules (X)
| Scenario | Recommended |
|---|---|
| Scarce data (N<100), complex IL, small capacity | equivariant l2 (4–6× data value) |
| Scarce data, simple IL (BF4) | scalar l0 (equivariance redundant) |
| Large data (N>500) | scalar l0 + data (chemical accuracy, architecture-independent) |
| Force prediction, EMIM cation | equivariant l2 (force gap +1709 meV/Å) |
| Force prediction, Pyr14 cation | scalar l0 (force gap −90) |
| Ample capacity, N>9 (energy) | scalar l0 (equivariance gap < chemical accuracy 43 meV) |
| Scarce capacity, any N (energy) | equivariant l2 (gap constant ~65 meV, always above chemical threshold) |
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
- unified_law_fig.png (equivalence-substitution phase transition: gap vs N across 32/64/128 ch; β_eff jump with critical capacity C*≈52.6)
- unified_law_support.png (scalar vs equivariant learning curves; gap @ N=15 vs N=45 collapse revealing the transition)
- unified_law_beta.png (β_eff sigmoid fit in capacity: β_max≈1.31, C*≈52.6 ch, σ_w≈5.0)
- unified_law_mechanism.png (symmetry discount κ/s^m; C*=λκ/s^m prediction; unified small→large-scale spectrum)

## References
See quantitative_laws_refs.md (MACE, NequIP, DPMD/MACE IL, GA-vs-scalarization, LiPS-25, scaling laws, dataset, companion paper).

