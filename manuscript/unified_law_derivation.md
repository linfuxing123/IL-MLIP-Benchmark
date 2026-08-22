# Unified scaling law — reproducible derivation (Supplementary)

## Setting
L(N, D, C; s, κ) = equivariance gap (measured as RMSE difference); N = configurations (data), D = tokens, C = capacity (channels), s = symmetry degree, κ = intrinsic problem complexity.

## 1. Symmetry discount (effective degrees of freedom)
Symmetry s reduces independent parameters (echoing arXiv:2502.05300, "symmetry controls the effective number of parameters"): N_eff = N_params / g(s) → effective complexity κ_eff = κ / s^m, with m the discount exponent (each order of symmetry compresses complexity by a factor of s).

## 2. Data–capacity competition (transition kernel)
β_eff (data exponent) describes how well data substitutes equivariance. Substitution is possible iff capacity C ≥ effective complexity κ_eff:
- C < κ_eff (capacity-scarce): data ineffective (β_eff = 0)
- C > κ_eff (capacity-ample): data effective (β_eff = β_max(s))

Smooth (sigmoid) transition: β_eff(C) = β_max(s)·σ((C − κ/s^m)/w).

## 3. Unified scaling law
L = L∞ + A_s·N^(−α(s)) + B_s·D^(−β_eff(C; s, κ))

Limits verified:
- C ≫ κ_eff (large-scale Ngo regime): σ→1 → β_eff = β_max → reduces to double power law (Ngo & Ravanbakhsh, ICLR 2026)
- C ≪ κ_eff (capacity-scarce): σ→0 → data term D^0 → gap constant (32-ch)

## 4. Calibration on Pyr14-FSI (per-atom official eval_configs)
| capacity | gap(N=15) | gap(N=45) | β_eff |
|---|---|---|---|
| 32 ch | 66.5 | 65.0 | 0.02 |
| 64 ch | 66.2 | 17.9 | 1.19 |
| 128 ch | 25.8 | 6.1 | 1.31 |

## 5. Sigmoid fit
β_eff(C) = β_max/(1+exp(−(C − C*)/σ_w)) with **β_max = 1.313, C* = 52.6 channels, σ_w = 4.99 (≈9% of C*)** → λκ/s^m ≈ 52.6 (for s = 2, Pyr14-FSI; σ_w/C* = 0.095).

## 6. Reproducible form for submission
L = L∞ + A_s·N^(−α(s)) + B_s·D^(−β_max(s)/(1+exp(−(C − λκ/s^m)/(λκ/s^m·σ_w))))
Pyr14-FSI calibration: β_max = 1.313, λκ/s^m = C* = 52.6, σ_w/C* = 0.095.
