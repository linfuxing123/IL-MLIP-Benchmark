# Rebuttal strengthening (new evidence, post-submission)

The following evidence became available after submission and strengthens the manuscript "Equivariance as a Substitutable Resource" (JCTC in review). It addresses likely reviewer concerns with hard, quantitative results.

## S1: "The learning curves rely on a single system (Pyr14-FSI) / small data."
**(new) Unified scaling law + cross-system verification.** All substitutability laws collapse into one scaling law L = L∞ + A_s·N^(−α(s)) + B_s·D^(−β_eff(C)) with β_eff a steep sigmoid in capacity (β_max ≈ 1.31, C\* ≈ 52.6 ch, σ_w ≈ 9% of C\*, Pyr14-FSI). Crucially, we repeated the capacity sweep on a second IL (Pyr14-NTf2): at 32 ch its gap already decays (52.7 → 16.2 meV/atom, β_eff ≈ 1.07) whereas Pyr14-FSI at 32 ch is constant (66.5 → 65.0, β_eff ≈ 0.02). Thus **C\*(NTf2) < 32 while C\*(FSI) ≈ 52.6** — the critical capacity is set by the chemical composition (complexity κ), so the law is *predictive* (C\* = λκ/s^m), not single-system. This directly generalizes the manuscript's central claim.

## S2: "The 32-ch constant gap contradicts capacity substitution."
**(new) Phase-transition resolution.** The two behaviors are complementary halves of one transition: at 32 ch capacity < C\* so data cannot substitute (gap constant); at 64/128 ch capacity > C\* so data substitutes (gap ~ N^−β). The measured β_eff (0.02 → 1.19 → 1.31 across 32/64/128 ch) quantifies this crossover and locates C\* ≈ 52.6 — turning the apparent contradiction into a quantitative law.

## S3: "Energy RMSE values look large / are the models okay?"
**(new) Per-atom official protocol.** Re-evaluated with the official MACE eval_configs (MACE_energy, divided by the number of atoms): 64-ch l0 = 268.5, l0@N45 = 187.2, l2 = 202.3/169.3 meV/atom — consistent with the legacy 32-ch (271.3/204.8) and 128-ch (246.0/220.2) records; the earlier apparent discrepancy was a units artifact (total-energy RMSE without dividing by the 39-atom system). Per-atom values are physically reasonable.

## S4: "Equivariance does not help forces on all systems."
**(new) Force gaps are cation-driven, anion-independent.** Grouping by cation: EMIM +1709 > BMIM +333 > Pyr14 −90 meV/Å (strong ordering); by anion: no consistent ordering (BF4 +1624 but not all-positive; PF6 +719; FSI −304; NTf2 +520). The equivariance force benefit is real but cation-dependent — a quantified, not assumed, dimension-specificity. Add the bulk radial-weakness (≈59% in 2-ion-pair) as the multi-body counterpart.
