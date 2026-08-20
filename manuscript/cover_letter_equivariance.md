[Date]

Dear Editor,

I am pleased to submit the manuscript "Equivariance as a Substitutable Resource: Data-Capacity-Complexity Trade-offs in Machine-Learning Interatomic Potentials for Ionic Liquids" for consideration in the *Journal of Chemical Information and Modeling*.

**Why this work matters.** Equivariant graph neural networks (MACE, NequIP) are the default for machine-learned interatomic potentials (MLIPs), yet the field lacks a clear answer to when equivariance is actually *required*. This manuscript settles the question with a controlled, reproducible study: within a single MACE framework (varying only the maximum angular momentum, l_max = 0 vs 2), across data sizes (15–45 configurations), channel capacities (32 vs 128), and 8 ionic liquids spanning a wide complexity range (BF4 to PF6), we show that the equivariance gap obeys a *substitutability law*:

ΔRMSE(l_max=0 − l_max=2) ≈ f(data volume, model capacity, system complexity, dimension),

where these resources are mutually substitutable. We further validate across force prediction (8 ILs, 3 seeds, 48 models — revealing a *dimension-specific* complexity dependence), a second architecture (NequIP), and a PAC-learning framework. A radial-cutoff scan rules out the truncation-compensation hypothesis.

**Key findings:**

1. **Substitutability law (energy):** The equivariance advantage is confined to the small-data regime (N = 15: +24.5 meV/atom on Pyr14-FSI, vanishing at N ≥ 30). At fixed data, the gap grows with capacity scarcity (32-channel: +66.5 vs 128-channel: +24.5 meV). Across 8 ILs, the energy gap scales with anion size (PF6 > FSI > NTf2 > BF4).

2. **Dimension-specific complexity dependence (forces):** Force prediction experiments across all 8 ILs (3 seeds each, 48 models total) reveal that the force gap is *cation-modulated* (all EMIM ILs show positive force gaps, +123 to +3347 meV/Å) rather than anion-driven (the energy pattern), and 4 of 8 ILs show opposite signs between energy and force gaps. Equivariance helps forces on simple systems (45% RMSE reduction on EMIM-BF4) but not on complex systems — the *opposite* of the energy pattern. This refutes the PAC-theory prediction that forces, as a 3N-dimensional vector field, should show larger gaps on complex systems.

3. **Practical guidance:** On simple ILs with adequate data, scalar MACE saves 7× parameters with no energy accuracy loss — but if force prediction is the goal, equivariant channels yield a 45% force RMSE reduction. On complex ILs with scarce data, equivariant channels are essential for energy but offer no force advantage.

**Contributions:**
1. First systematic l_max ablation within one architecture (MACE) isolating equivariance from architecture changes
2. A substitutability law unifying the "equivariance is unnecessary" (simple systems) and "equivariance scales better" (large data) findings
3. Discovery of dimension-specific complexity dependence: energy gap is anion-driven, force gap is cation-modulated — a previously unreported dichotomy
4. Fully reproducible: data (8 ILs, 435 configurations with B3LYP/STO-3G forces), 48 trained models, and all scripts on GitHub (v1.7.2) and Zenodo (10.5281/zenodo.22027477)

The manuscript is original, has not been published elsewhere, and is not under consideration by another journal.

I am the sole and corresponding author. Thank you for your consideration.

Sincerely,
Fuxing Lin
Hunan Institute of Engineering
3612411485@qq.com · ORCID 0009-0003-7588-6942
