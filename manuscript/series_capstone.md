# IL-MLIP / Equivariant MLIP Research Series — Capstone Summary

**Principal investigator**: Fuxing Lin, Hunan Institute of Engineering
**Series window**: 2026-08 (multi-session, consolidated)
**Repository**: github.com/linfuxing123/IL-MLIP-Benchmark (main)

## Publications in the series

| # | Title | Status | Venue |
|---|---|---|---|
| 1 | IL-MLIP-Benchmark: A Benchmark Dataset and Energy-Decomposition Analysis for Ionic Liquid MLIPs | published/prepared | (dataset + EDT) |
| 2 | Message Passing, Not Equivariance: Why MACE Outperforms SchNet on Ionic Liquids | prepared | JCTC (methods) |
| 3 | Equivariance as a Substitutable Resource: Data–Capacity–Complexity Trade-offs in MLIPs for Ionic Liquids | **under review** | JCTC |
| 4 | Quantitative Laws of Equivariance Substitutability in IL-MLIPs | **submission-ready** | JCTC |

## Fourteen quantitative laws (paper 4, per-IL reliability flagged)

1. Data-substitution power law: gap ~ 1109.5 × N^−1.49 (128 ch); constant ~65 meV (32 ch)
2. Data-efficiency: equivariance = 4–6× data (capacity-scarce); 1.2× (ample)
3. Capacity-substitution: 4× capacity replaces 61–91% of equivariance need
4. Radial-dominance (forces): 59–99% radial (8 ILs); ~59% bulk
5. Cation-modulated force gaps: EMIM +1709 > BMIM +333 > Pyr14 −90 meV/Å (anion-independent)
6. PAC calibration: empirical substitution 3–4× faster than worst-case bound
7. Energy generalization: accuracy = f(force supervision, coverage, span)
8. Normalized energy metric (RMSE/span): v5 3.7‰ vs 8-IL 34–190‰
9. Bulk equivariance: l2 79 vs l0 122 meV/Å (+35%)
10. Chemical-accuracy crossover: N > 9 at 128 ch; never at 32 ch
11. Simple vs complex: gap ≈ 0 (simple); positive + decaying (complex)
12. Seed robustness: 4/8 sign-stable; force RMSE seed std 3–26%
13. Dimension-specificity: force cation-ordered, energy anion-weak
14. Bulk force power law: RMSE = 1895 × N^−0.66; MD needs ~2700 frames (STO-3G)

## Environment & generalization theory (rounds 4–5, honest split)

- Forces generalize robustly (local gradients; 8-IL 269→91 meV/Å stable across seeds/spans)
- Energy is sampling-sensitive (global integral): accurate in-distribution with force supervision (v5: 67 meV), poor on extrapolation (50 eV on large-displacement)
- e3nn 0.6 force-free ef training underfits energy (9594 meV) vs legacy e3nn 0.5 (246) — a training-behavior difference, not intrinsic failure
- Normalized metric (RMSE/span) enables fair cross-system comparison
- Sampling must cover the target energy surface (BQ/BZ: 59-frame near-equilibrium model fails to extrapolate to large displacements)

## Datasets

- 8 ILs × 435 conformations (B3LYP/STO-3G) + per-atom forces (8 ILs)
- Bulk 2-ion-pair EMIM-BF4: 59 frames (near-equilibrium) + 30 large-displacement frames (in progress)
- 8-IL force radial fractions, force-8IL comparison, learning curves (32/128 ch)

## Deliverables in repo

- manuscript/: next_paper_quantitative_laws.md (+ .docx), refs, summary, cover letter, rebuttal prep, revised SI table
- lc_equivariance/: 5 figures + quantitative_laws data
- data/: bulk datasets, radial data, force comparison

## Next steps

1. Await equivariance-paper review → revise per rebuttal_prep.md
2. Submit quantitative-laws paper to JCTC
3. Complete large-displacement bulk DFT (30 frames) → filter outliers → retrain to cover high-energy surface
