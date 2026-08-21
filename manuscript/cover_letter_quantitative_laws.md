[Date]

Dear Editor,

I am pleased to submit the manuscript "Quantitative Laws of Equivariance Substitutability in Ionic-Liquid Machine-Learned Interatomic Potentials" for consideration in the *Journal of Chemical Theory and Computation*.

**Why this work matters.** Equivariant neural network interatomic potentials dominate ionic-liquid (IL) modeling, yet *how* their advantage scales with data, capacity, and composition has remained qualitative. This manuscript derives the first quantitative laws of equivariance substitutability from a controlled MACE l_max ablation (0 vs 2) across 8 ILs, multiple data sizes, and channel capacities:

1. **Data-substitution power law**: the equivariance gap decays as ~N^-1.49 with data volume when capacity is sufficient (128 ch), but saturates at a constant ~65 meV when capacity is scarce (32 ch) — data substitutes equivariance only when capacity is available.

2. **Data-efficiency law**: under capacity scarcity, equivariant models provide 4.0–5.8× data efficiency (15 frames = 60 scalar frames; 45 = 262), collapsing to 1.2× at sufficient capacity.

3. **Radial-dominance law (forces)**: force prediction error is 59–99% radial across 8 ILs; equivariance primarily improves force *magnitude* prediction, not direction (weakening to ~59% in bulk — multi-body effects).

4. **Capacity-substitution law**: 4× capacity replaces 61–91% of the equivariance need (N=45: 91%).

5. **Cation-modulated force gaps, quantified**: mean force gap ranks EMIM (+1709 meV/Å) > BMIM (+333) > Pyr14 (−90).

6. **PAC calibration**: empirical data-substitution rate is 3–4× faster than the PAC worst-case bound.

7. **Energy generalization theory**: energy accuracy = f(force supervision, training coverage, test span) — normalized metric (RMSE/span) introduced; force generalization is robust, energy is sampling-sensitive (bulk energy learning curve: 502→74 meV over 7→59 frames).

These laws make equivariance substitutability quantitative and predictive, providing direct practical guidance (decision rules) for MLIP deployment on ILs under limited data or compute budgets.

The manuscript is original, has not been published elsewhere, and is not under consideration by another journal. I am the sole and corresponding author.

Sincerely,
Fuxing Lin
Hunan Institute of Engineering
3612411485@qq.com · ORCID 0009-0003-7588-6942
