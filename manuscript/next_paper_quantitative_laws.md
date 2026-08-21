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

### 3.3 Radial-dominance law (B2)
- Force error radial-dominated across all 8 ILs (59–99% radial; EMIM-BF4 98.8%, BMIM-PF6 74–59%)
- Equivariance cuts radial (magnitude) error most (EMIM-BF4: −60%), tangential (direction) less
- **Equivariance improves force magnitude primarily; direction error secondary, system-dependent**

### 3.4 Cation-modulated force gaps, quantified (B5)
- Mean force gap: EMIM +1709 > BMIM +333 > Pyr14 −90 meV/Å
- Seed robustness: 4/8 ILs sign-stable across 3 seeds; mean ranking robust

### 3.5 Simple vs complex (B7)
- Simple (EMIM-BF4): gap ≈ 0 (noise); complex (Pyr14-FSI): positive + decaying
- Scalar learning exponent: complex −0.40 vs simple −0.30 (data more valuable on complex)

## 4. Discussion
- Unified picture: equivariance = symmetry prior worth 4–6× data when capacity-scarce, ~1.2× when capacity-free; force benefit = magnitude (radial), not direction
- Practical guidance: scalar MACE + data for simple ILs; equivariant for complex/scarce-data
- Limitations: STO-3G level, single architecture family (MACE), isolated-ion-pair force analysis

## 5. Data availability
- GitHub linfuxing123/IL-MLIP-Benchmark (v1.7.2+) + Zenodo 10.5281/zenodo.22027477
- Analysis scripts: workspace/chem-library (b1–b7, d1)

## Figures
- quantitative_laws_fig.png (power law, data efficiency, radial dominance)
