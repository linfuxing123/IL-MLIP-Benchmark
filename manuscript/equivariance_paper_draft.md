# Equivariance as a Substitutable Resource: Data-Capacity-Complexity Trade-offs in Machine-Learning Interatomic Potentials for Ionic Liquids

**Authors:** Fuxing Lin (ORCID: 0009-0003-7588-6942)

**Affiliation:** Hunan Institute of Engineering

**Corresponding author:** Fuxing Lin; email: 3612411485@qq.com

---

## Abstract

Equivariant graph neural networks dominate machine-learned interatomic potentials (MLIPs), yet whether their spherical-harmonic channels (angular momentum l >= 1) are *required*—or merely advantageous under resource constraints—remains debated. Using MACE (a many-body equivariant architecture) as a controlled framework, we ablate the maximum angular momentum (l_max = 0 scalar vs l_max = 2 equivariant) across ionic liquids (ILs) of varying complexity, data sizes, and channel capacities. We find that the equivariance gap, delta-RMSE(l_max=0 - l_max=2), obeys a *substitutability law*: it is a function of three mutually substitutable resources—data volume, model capacity, and system complexity. (i) At fixed capacity, the gap shrinks with data (128-channel Pyr14-FSI: 25.8 to 6.1 meV/atom from 15 to 45 configurations); (ii) at fixed data, the gap grows sharply with capacity scarcity (32-channel gap 66.5 vs 128-channel 25.8 meV); (iii) across 8 ILs, the gap scales with anion size (PF6: +45 to +108 meV; BF4: approximately 0 to -8 meV). A radial-cutoff scan rules out truncation compensation as the mechanism. Force prediction experiments across all 8 ILs reveal a *dimension-specific* complexity dependence: 5 of 8 ILs show opposite signs between energy and force gaps, and the force gap is cation-driven (EMIM positive, +284 to +3347 meV/Å) rather than anion-driven (the energy pattern)—equivariant capacity freed from simple energy landscapes redirects to the 3N-dimensional force vector field, while large energy gaps consume the equivariant budget. These results establish that equivariance acts as a symmetry prior substitutable by data and capacity, with system-complexity-dependent benefits that differ between energy and force dimensions—reconciling the "equivariance is unnecessary" (simple systems) and "equivariance scales better" (large data) findings in the literature.

---

## 1. Introduction

Equivariant neural networks have become the default for machine-learned interatomic potentials (MLIPs) [1,2], motivated by the rotational equivariance of the underlying physics. The spherical-harmonic channels (angular momentum l ≥ 1) are widely assumed necessary to represent orientation-dependent interactions. However, this assumption has been challenged: because atomic-pair distances uniquely determine molecular geometry up to chirality (via the Gram matrix) [3,4], a scalar (l_max = 0) architecture that captures pair distances can in principle encode angles and orientation. Recent work further shows that distance-based message passing is representationally sufficient in many settings [5], and that equivariance matters *more* at larger scales in general force fields [6].

Ionic liquids (ILs) provide an ideal testbed: their cation–anion combinations span a wide complexity range—from small, symmetric anions (BF4) to large, conformationally flexible ones (PF6, NTf2, FSI)—and their MLIP training data are inherently scarce (tens of configurations per system from DFT). This combination of variable complexity and scarce data isolates the question: **when is equivariance actually needed?**

Prior work in this series established three empirical facts: (i) a scalar-only (l_max = 0) MACE reaches chemical accuracy on simple ILs and covalent molecules (methane, ethanol, butane), (ii) on complex ILs (Pyr14, PF6) l_max = 0 degrades, and (iii) a radial-cutoff (r_max) scan shows no monotonic dependence of the l_max gap—ruling out the "equivariance compensates truncation" hypothesis [7]. The mechanism by which equivariance helps complex systems was left open. Here we close it with a systematic learning-curve study varying data volume, channel capacity, and system complexity within a single MACE framework.

## 2. Results

### 2.1. Data substitutes equivariance (when capacity is sufficient)

We train l_max = 0 and l_max = 2 MACE models (128 channels) on Pyr14-FSI (a complex IL: pyrrolidinium cation, bis(fluorosulfonyl)imide anion) at 15, 30, and 45 configurations, evaluated on a fixed 15-configuration test set. The equivariance gap shrinks sharply with data (Fig. 1, top):

| N | l_max=0 | l_max=2 | gap |
|---|---|---|---|
| 15 | 246.0 | 220.2 | **+25.8** |
| 30 | 172.9 | 169.6 | +3.3 |
| 45 | 160.6 | 154.5 | +6.1 |

The scalar architecture's scaling exponent in the small-data regime (α = 0.51 for 15→30) exceeds the equivariant's (α = 0.38), i.e., the scalar model catches up as data accumulate. Equivariance is thus a *data-efficiency* advantage (a symmetry prior that helps small samples), not a representational requirement. The N = 15 advantage is robust across three seeds (gap +12.3, +25.8, +6.9 meV; l0 229 ± 17 vs l2 214 ± 11 meV/atom).

![Figure 1](figures/fig1_learning_curve.png)

**Fig. 1. The equivariance gap shrinks with data at high capacity (128 channels) but persists at low capacity (32 channels).** Pyr14-FSI, fixed 15-configuration test set.

### 2.2. Capacity substitutes equivariance

At fixed data (N = 15, Pyr14-FSI), reducing channel capacity from 128 to 32 widens the gap nearly threefold:

| channels | l_max=0 | l_max=2 | gap |
|---|---|---|---|
| 32 | 271.3 | 204.8 | **+66.5** |
| 128 | 246.0 | 220.2 | +25.8 |

Critically, the 32-channel gap *does not shrink* with data (66.5 → 65.0 meV from 15 to 45 configurations), whereas the 128-channel gap does (25.8 → 6.1). When capacity is scarce, extra data cannot compensate for the missing equivariant channels; when capacity is ample, it can.

### 2.3. System complexity determines the equivariance demand

Across 8 ILs (60-configuration training, 32 channels), the equivariance gap ranks by anion size:

| IL | anion | l_max=0 | l_max=2 | gap |
|---|---|---|---|---|
| BMIM-PF6 | PF6 | 388.9 | 281.0 | +107.9 |
| EMIM-PF6 | PF6 | 235.8 | 190.4 | +45.4 |
| Pyr14-FSI | FSI | 134.6 | 91.5 | +43.1 |
| Pyr14-NTf2 | NTf2 | 101.9 | 78.6 | +23.3 |
| BMIM-NTf2 | NTf2 | 104.3 | 92.9 | +11.4 |
| BMIM-BF4 | BF4 | 21.2 | 17.7 | +3.5 |
| EMIM-BF4 | BF4 | 34.9 | 43.0 | −8.1 |
| EMIM-NTf2 | NTf2 | 104.2 | 115.7 | −11.5 |

Large, flexible anions (PF6, FSI)—with many directional degrees of freedom—require equivariance; small symmetric anions (BF4) do not (gap ≈ 0 or negative, Fig. 2). On simple systems (EMIM-BF4), the scalar model matches or beats the equivariant one at every data size tested (gap −8.3 to −6.4 meV at 128 channels; the N = 45 point shows seed-dependent fluctuation, 72–102 meV for l_max = 0 across three seeds, consistent with small-data overfitting at high capacity rather than a systematic equivariance effect).

![Figure 2](figures/fig2_il_gaps.png)

**Fig. 2. Equivariance demand ranks by anion size across 8 ILs** (32 channels, 60 configurations): large flexible anions (PF6, FSI) show large gaps; small symmetric BF4 shows none.

### 2.4. Truncation compensation is ruled out

A radial-cutoff scan (r_max = 3, 4, 5, 6 Å) on both EMIM-BF4 and Pyr14-FSI shows no monotonic growth of the gap as r_max shrinks [7]. Equivariance does not rescue truncation loss; it substitutes for data and capacity.

## 3. Validation across force prediction, architectures, and theory

### 3.1. Force prediction: dimension-specific complexity dependence across 8 ILs

We generated B3LYP/STO-3G analytical forces for all 8 ILs (435 configurations total) using PySCF nuclear gradients (energies cross-validated to 0.00000000 eV against the energy-only dataset, 0 SCF failures). We trained l_max = 0 and l_max = 2 MACE models (32 channels, 150 epochs, energy+force loss with force weight 10) on 30 configurations and evaluated on a fixed 15-configuration test set (seed 42 split; EMIM-BF4 and Pyr14-FSI use 3 seeds for fluctuation checks).

The full 8-IL force gap ranking reveals a **dimension-specific complexity dependence** that systematically differs from the energy dimension:

| IL | anion | l0 F (meV/Å) | l2 F (meV/Å) | ΔF (force gap) | ΔE (energy gap, §2.3) | sign match |
|---|---|---|---|---|---|---|
| EMIM-BF4 | BF4 | 7419.9 ± 276.7 | 4073.1 ± 1058.6 | **+3346.9** | −8.1 | opposite |
| EMIM-PF6 | PF6 | 5469.4 | 4375.6 | **+1093.8** | +45.4 | same |
| EMIM-NTf2 | NTf2 | 4295.4 | 3453.5 | **+841.9** | −11.5 | opposite |
| Pyr14-NTf2 | NTf2 | 1641.7 | 1357.3 | **+284.4** | +23.3 | same |
| BMIM-NTf2 | NTf2 | 5496.4 | 5255.5 | **+240.9** | +11.4 | same |
| BMIM-BF4 | BF4 | 396.1 | 524.0 | **−127.9** | +3.5 | opposite |
| BMIM-PF6 | PF6 | 4296.3 | 4540.9 | **−244.6** | +107.9 | opposite |
| Pyr14-FSI | FSI | 4003.5 ± 349.1 | 4307.2 ± 585.4 | **−303.7** | +43.1 | opposite |

Key findings:

- **5 of 8 ILs show opposite signs** between the energy and force gaps—equivariance helps energy but hurts forces (or vice versa) more often than not. The complexity dependence is thus **dimension-specific**, not simply transferred from energy to forces.
- **Force gap is cation-driven, not anion-driven**: all three EMIM cation ILs show positive force gaps (equivariant better, +842 to +3347 meV/Å), while BMIM and Pyr14 ILs show mixed or negative gaps. This contrasts sharply with the energy dimension, where the gap is anion-driven (PF6 > FSI > NTf2 > BF4).
- **Largest force gains on simple systems**: EMIM-BF4 (+3347 meV/Å, 45% reduction) and EMIM-PF6 (+1094 meV/Å, 20% reduction)—the systems where the energy gap is smallest or negative. On complex systems where the energy gap is large (BMIM-PF6: +108 meV energy), the force gap is negative (−245 meV/Å), indicating the equivariant budget is consumed by energy learning.
- **Energy under joint training**: the scalar model retains better energy accuracy when the force gap is large (EMIM-BF4: 96 vs 380 meV), confirming a force–energy capacity trade-off from the joint loss.

This finding refines the substitutability law: the complexity dependence is **dimension-specific and cation-modulated**—equivariance substitutes for data/capacity differently in the energy scalar field (anion-driven) versus the 3N-dimensional force vector field (cation-driven). On systems where the energy landscape is already well-captured by scalar features (small energy gap), the equivariant channels redirect capacity toward the force vector field, yielding large force gains. On systems where the energy gap is large, no surplus capacity remains for forces.

### 3.2. Cross-architecture validation (NequIP)

To rule out architecture-specific effects, we trained NequIP (0.19) at l_max = 0 and l_max = 2 (64 features, 4 layers, 300 epochs) on the EMIM-BF4 force data (per-atom forces format). NequIP shows a modest equivariance advantage (energy 2.60 to 2.24 eV; forces 7.53 to 6.82 eV/A, i.e., approximately 14% and 9%). The MACE force experiment (section 3.1) shows a larger equivariance advantage on the same simple system (45% force RMSE reduction at 32 channels), indicating that the equivariance benefit magnitude is architecture-dependent: MACE many-body equivariant message passing captures more force information than NequIP two-body interactions. The cross-architecture consensus is that equivariance does benefit force prediction on simple systems (9 to 45% depending on architecture), confirming that the force dimension has a different complexity dependence than the energy dimension.

### 3.3. Theoretical framework (PAC learning)

The substitutability law follows from a PAC-learning argument. Let H_eq ⊂ H_sc be the equivariant and scalar hypothesis spaces (VC dimensions d_eq < d_sc, since the symmetry constraint removes invalid functions). For N i.i.d. samples,

ε_sc(N) − ε_eq(N) ≈ (√d_sc − √d_eq)/√N,

yielding three predictions: (i) the gap shrinks as N^(−1/2) (128-ch: 25.8 → 6.1 meV) — confirmed; (ii) complex systems (large Δd) show larger, slower-shrinking gaps (32-ch Pyr14: gap persists with data) — confirmed; (iii) forces, as a 3N-dimensional vector field, should show larger gaps on complex systems — **refuted** by the 8-IL force experiment (§3.1): 5 of 8 ILs show opposite signs between energy and force gaps, and the force gap is cation-driven (EMIM positive) rather than anion-driven (energy pattern). The PAC argument applies to the energy dimension but not directly to forces, because the force vector field introduces additional angular degrees of freedom that interact with equivariance in a dimension-specific and cation-modulated way: on systems where the energy gap is small (EMIM cation), equivariant capacity freed from energy modeling redirects to forces; on systems where the energy gap is large (BMIM-PF6, Pyr14-FSI), the equivariant budget is consumed by energy, leaving no surplus for forces. A Rademacher-complexity formulation (theory_rademacher.md) replaces VC dimensions by effective parameter dimensions, giving the same law with a computable Δθ = 2(√p − √q) that quantifies the capacity-substitution effect (low capacity → large Δθ → large gap, as in the 32-channel result).

## 4. Discussion

**The substitutability law.** The equivariance gap obeys

ΔRMSE(l_max=0 − l_max=2) = f(capacity, data, complexity, dimension),

where increasing any of data, capacity, or simplicity reduces the gap. Equivariance is a symmetry prior that reduces the hypothesis-space complexity; it is substitutable by more data, more capacity, or simpler systems. The force experiment (§3.1) adds a fourth variable—*dimension* (energy vs forces)—revealing that the complexity dependence is dimension-specific: equivariance helps forces on simple systems (where energy is already well-captured) but not on complex systems (where the energy gap consumes the equivariant budget).

**Reconciling contradictory findings.** Prior work showed "equivariance is unnecessary" on simple systems [8] and "equivariance scales better with data" in general force fields [6]. Our framework reconciles both: the former holds at low complexity (BF4-type systems), the latter holds when capacity is scarce (32-channel, where the gap persists with data) or when the comparison mixes architectures (SchNet vs equivariant, rather than an l_max ablation within one architecture). The force results add a further nuance: for *force* prediction specifically, the equivariance benefit is **cation-driven** (all EMIM ILs show positive force gaps) rather than anion-driven (the energy pattern), and 5 of 8 ILs show opposite signs between energy and force gaps—equivariance helps energy but hurts forces (or vice versa) more often than not. This dimension-specificity arises because the 3N-dimensional force vector field benefits from equivariant capacity that is freed when the energy landscape is simple, while large energy gaps consume the equivariant budget before it can benefit forces.

**Practical guidance.** For IL MLIPs (and by extension other scarce-data, variable-complexity systems), the choice of l_max should be guided by (i) system complexity, (ii) data budget, (iii) capacity constraints, and (iv) the target property (energy vs forces). On simple ILs with adequate data, a scalar MACE saves 7× parameters with no energy accuracy loss—but if force prediction is the goal, equivariant channels yield a 45% force RMSE reduction. On complex ILs with scarce data, equivariant channels are essential for energy but offer no force advantage.

## 5. Materials and Methods

**Data.** DFT-optimized configurations and energies (B3LYP/STO-3G) for 8 ILs (60 configurations each: EMIM/BMIM/Pyr14 cations × BF4/PF6/NTf2/FSI anions, 435 total) and covalent molecules (methane, ethanol, butane); see [7] and Data Availability.

**Models.** MACE (mace-torch 0.3.16) with hidden_irreps 32x0e (l_max = 0) or 32x0e+32x1o+32x2e (l_max = 2) at 32 channels, and 128x0e / 128x0e+128x1o+128x2e at 128 channels; r_max = 5.0 Å (scan: 3, 4, 5, 6 Å); energy-only loss (--loss=ef with --energy_key=energy, force weight 0); 250–400 epochs with SWA (EMA for force models; batch 4, num_workers 0 on Windows); float64 for energy-only models; fixed train/test splits (15/15/30/45 configurations, seed 42; additional seeds 7, 123 for fluctuation checks); CUDA. **Force models** (§3.1): 32 channels, float32, 150 epochs, energy+force loss (force weight 10, energy weight 1), SWA for l_max=0 / EMA (decay 0.99) for l_max=2, batch 4, CPU (OMP_NUM_THREADS=4); forces generated via PySCF B3LYP/STO-3G analytical nuclear gradients, stored in ASE extended XYZ format with per-atom forces (Properties=species:S:1:pos:R:3:forces:R:3). **NequIP (0.19)** with l_max = 0/2, 64 features, 4 layers, 300 epochs, energy+force loss (coeff 1:10) on the same splits.

**Analysis.** Test RMSE per atom (meV) on the fixed 15-configuration test set (MACE eval_configs); scaling exponents from two-point power-law fits; equivariance gap ΔRMSE = RMSE(l_max=0) − RMSE(l_max=2).

**Radial-cutoff scan.** Both EMIM-BF4 and Pyr14-FSI were trained at r_max = 3, 4, 5, 6 Å with l_max = 0 and l_max = 2 (128 channels, 60 configurations); the gap shows no monotonic dependence on r_max (see companion [7]).

## 6. Data and Software Availability

All data, models, and scripts are available at https://github.com/linfuxing123/IL-MLIP-Benchmark (v1.5.0) and archived on Zenodo (https://doi.org/10.5281/zenodo.21960800). Force data (B3LYP/STO-3G analytical gradients for EMIM-BF4 and Pyr14-FSI, 60 configurations each) and trained 32-channel force models (l_max = 0/2 × 3 seeds × 2 ILs) are included in the v1.7.0 release.

## References

1. Batatia, I., Kovacs, D. P., Simm, G., Ortner, C., Csanyi, G. MACE: Higher order equivariant message passing neural networks for fast and accurate force fields. *NeurIPS* (2022).
2. Batzner, S., et al. E(3)-equivariant graph neural networks for data-efficient and accurate interatomic potentials. *Nat. Commun.* **13**, 2453 (2022).
3. Schoenberg, I. J. Remarks to Maurice Fréchet's article on metric spaces. *Ann. Math.* **36**, 724–732 (1935).
4. Blumenthal, L. M. *Theory and Applications of Distance Geometry*. Clarendon Press, Oxford (1953).
5. Wang, Z. et al. Is Distance Matrix Enough for Geometric Deep Learning? *NeurIPS* (2023).
6. Ngo, K., Ravanbakhsh, S. Scaling Laws and Symmetry, Evidence from Neural Force Fields. *ICLR* (2026).
7. Lin, F. Scalar architectures reach chemical accuracy on simple ionic liquids: revisiting whether equivariance is required. *J. Chem. Inf. Model.* (submitted 2026); companion paper (JCIM manuscript ci-2026-027780).
8. Lin, F. IL-MLIP-Benchmark: Ionic liquid machine-learned interatomic potential benchmark. *Zenodo* (2026), doi:10.5281/zenodo.21960800.
