# Quantitative Laws of Equivariance Substitutability in Ionic-Liquid Machine-Learned Interatomic Potentials

## Abstract (draft)

Equivariant neural network interatomic potentials (MACE, NequIP) dominate ionic-liquid (IL) modeling, yet *how* their advantage scales with data, capacity, and system composition has not been quantified. Building on a controlled l_max ablation (0 vs 2) across 8 ILs, we derive three quantitative laws:

1. **Data-substitution power law**: the equivariance energy gap decays as gap ~ N^-1.49 with data volume when capacity is sufficient (128 channels), but saturates at a constant ~65 meV when capacity is scarce (32 channels) — data volume substitutes equivariance only when capacity is available.

2. **Data-efficiency law**: under capacity scarcity, equivariant models provide a 4.0–5.8× data-efficiency gain (15 frames = 60 scalar frames; 45 = 262), collapsing to 1.2× at sufficient capacity.

3. **Radial-dominance law (forces)**: force prediction error is 95–99% radial (along the reference force direction) for both architectures; equivariance reduces radial (magnitude) error by 60% but leaves tangential (direction) error nearly unchanged — equivariance improves *force magnitude* prediction, not direction.

A fourth empirical regularity quantifies the cation modulation of force gaps: mean force gap (l_max=0 − l_max=2) ranks EMIM (+1709 meV/Å) > BMIM (+333) > Pyr14 (−90), confirming that equivariance's force benefit is cation-controlled, not anion-driven.

These laws make the substitutability of equivariance — by data, capacity, and composition — quantitative and predictive, providing practical guidance for MLIP deployment on ILs under limited data or compute budgets.

## Key numbers
- gap ~ 1109.5 × N^-1.49 (Pyr14-FSI, 128 ch); 66.5→65.0 meV (32 ch, constant)
- Data efficiency: 4.03× (N=15, 32 ch) → 5.82× (N=45); 1.25× (128 ch)
- Force error radial fraction: 98.8% (l0) / 94.8% (l2); tangential −13% only
- Force gap by cation: EMIM +1708.8 / BMIM +332.6 / Pyr14 −90.2 meV/Å

## Status
- Draft abstract — candidates: JCTC companion, JCIM, Digital Discovery (OA check)
- Data: existing 8-IL benchmark + new bulk 2-ion-pair dataset (in progress)
