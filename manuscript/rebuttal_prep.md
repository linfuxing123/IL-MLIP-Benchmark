# Rebuttal preparation for "Equivariance as a Substitutable Resource" (JCTC under review)

## Likely reviewer comments and prepared responses (based on this series' findings)

### R1: "The learning curves use only 3 N points (15/30/45) — the power-law exponent is unreliable."
**Response**: Agreed; the exponent −1.49 has medium confidence (N=30 is a seed outlier). We (i) report the 3-point fit with residual 4.4 meV, (ii) note the qualitative law (decay at 128 ch vs constant at 32 ch) is robust across points, (iii) provide the bulk learning curve (7→59 frames) as an independent confirmation of data-driven scaling, and (iv) plan denser N sampling (20/25/35/40) in revision.

### R2: "The 32-channel gap (~65 meV constant) contradicts 'capacity substitutes equivariance'."
**Response**: They are complementary: at 32 ch, capacity is the binding constraint, so data cannot substitute equivariance (gap constant); at 128 ch, capacity is ample, so data substitutes (gap ~ N^-1.49). The capacity-substitution law (4× capacity → 61–91% gap reduction) quantifies the crossover.

### R3: "Energy RMSE values are much larger than typical MLIP benchmarks — are the models trained correctly?"
**Response**: The large values reflect test-extrapolation (test spans 29–81 eV in the 8-IL single-pair data). In-distribution energy is accurate (bulk v5: 67 meV over 18-eV span; normalized RMSE/span 3.7‰ vs 34–190‰ for extrapolated tests). We introduce the normalized metric for fair comparison.

### R4: "Why does equivariance not help forces on all systems?"
**Response**: Force gaps are cation-modulated: EMIM +1709 > BMIM +333 > Pyr14 −90 meV/Å (mean, 3 seeds); 4/8 ILs are sign-stable. Equivariance's force benefit is real but system-dependent — quantified, not assumed.

### R5: "The force error decomposition (radial-dominant) is a single-system observation."
**Response**: Extended to all 8 ILs (59–99% radial; EMIM-BF4 98.8% extreme, BMIM-PF6 74–59% weak) and to bulk (~59% — multi-body direction effects). Direction quality (cos) improves with equivariance in 7/8 ILs.

## Prepared additional analyses (done in this series)
- 8-IL force radial fractions (force_radial_8il.json)
- Cation ranking + seed robustness (D1)
- Normalized energy metric (AK) + bulk energy learning curve (AL)
- Bulk 2-ion-pair dataset (59 frames) + learning curves
