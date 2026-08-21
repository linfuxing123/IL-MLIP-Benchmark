# IL-MLIP-Benchmark

First benchmark dataset of ionic liquid machine-learned interatomic potentials.

## Dataset
- **8 IL cation–anion pairs** (EMIM/BMIM/Pyr14 × BF4/PF6/NTf2/FSI)
- **435 clean conformations**, B3LYP/STO-3G energies (forces for EMIM-BF4)
- Location: `data/il_benchmark_clean/` (JSONL, one conformation per line)

## Key results
| Metric | Value |
|---|---|
| MACE fine-tuning (single IL, 5-fold CV) | 23.3 ± 5.8 meV/atom |
| Cross-IL generalization (leave-one-IL-out) | mean 37.6 meV/atom |
| Force RMSE (EMIM-BF4) | 640.8 meV/Å |
| From-scratch SchNet baseline | 6115.7 meV/atom (263× worse) |
| Ion rigidity (EDT) | E_cation 54 / E_anion 14 meV |

## Quantitative laws (equivariance substitutability)
| Law | Finding |
|---|---|
| Data-substitution power law | equivariance gap ~ N^−1.49 (128 ch); constant ~65 meV (32 ch) |
| Data-efficiency law | equivariance = 4.0–5.8× data when capacity-scarce (32 ch); 1.25× (128 ch) |
| Radial-dominance law | force error 95–99% radial; equivariance cuts magnitude (radial) not direction |
| Cation ranking (forces) | mean force gap EMIM +1709 > BMIM +333 > Pyr14 −90 meV/Å |
| PAC calibration | empirical data-substitution rate 3–4× faster than PAC bound |

See `manuscript/next_paper_quantitative_laws.md` for the full draft.

## Files
- `manuscript_il_mlip.md` — manuscript
- `manuscript/next_paper_quantitative_laws.md` — quantitative laws paper draft
- `cover_letter.md` — cover letter
- `data/il_mlip_benchmark.zip` — packaged dataset
- `workspace/chem-library/` — generation/filter/training/evaluation scripts
- `lc_equivariance/quantitative_laws_fig.png` — laws figure

## Citation
Lin, F. IL-MLIP-Benchmark: A Benchmark Dataset and Energy-Decomposition Analysis
for Ionic Liquid Machine-Learned Interatomic Potentials. 2026.

## License
MIT
