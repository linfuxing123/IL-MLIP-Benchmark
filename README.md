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

## Files
- `manuscript_il_mlip.md` — manuscript
- `cover_letter.md` — cover letter
- `data/il_mlip_benchmark.zip` — packaged dataset
- `workspace/chem-library/` — generation/filter/training/evaluation scripts

## Citation
Lin, F. IL-MLIP-Benchmark: A Benchmark Dataset and Energy-Decomposition Analysis
for Ionic Liquid Machine-Learned Interatomic Potentials. 2026.

## License
MIT
