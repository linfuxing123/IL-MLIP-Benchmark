# Equivariance as a Substitutable Resource — Learning Curve Data

Companion data for: *Equivariance as a Substitutable Resource: Data-Capacity-Complexity Trade-offs in Machine-Learning Interatomic Potentials for Ionic Liquids*.

## Core Finding

The equivariance gap ΔRMSE(l_max=0 − l_max=2) obeys a substitutability law — it is a function of three mutually substitutable resources: **data volume, model capacity, and system complexity**.

## Data

- `learning_curve_results.json` — all test RMSE values and gaps
- `data_pyr14_fsi/` — Pyr14-FSI train/test splits (15/15/30/45 configurations)
- `data_emim_bf4/` — EMIM-BF4 train/test splits

## Key Numbers (meV/atom, fixed 15-frame test)

### Pyr14-FSI (complex IL)

| channels | N=15 gap | N=45 gap |
|---|---|---|
| 32 | +66.5 | +65.0 (no shrink) |
| 128 | +25.8 | +6.1 (shrinks) |

### EMIM-BF4 (simple IL, 128ch)

gap ≈ −8 to −6 meV (equivariance redundant)

### 8 IL complexity ranking (32ch, 60 cfg)

PF6 (+45 to +108) > FSI (+43) > NTf2 (±11) > BF4 (≈0 to −8)

## Methods

MACE (mace-torch 0.3.16), hidden_irreps 32x0e / 32x0e+32x1o+32x2e (32ch) or 128x0e / 128x0e+128x1o+128x2e (128ch), r_max = 5.0 Å, energy-only, 250–400 epochs + SWA, float64, CUDA.

## Reproduce

```bash
# train l_max=0, 128ch, 15 configs
python -u -X utf8 run_train.py --name=pyr14_l0_n15 \
  --train_file=data_pyr14_fsi/train_15.xyz --valid_file=data_pyr14_fsi/test_15.xyz \
  --hidden_irreps=128x0e --r_max=5.0 --batch_size=4 --max_num_epochs=400 \
  --swa --loss=ef --energy_key=energy --default_dtype=float64 --device=cuda

# evaluate
python -u -X utf8 eval_configs.py --model=<model> --configs=data_pyr14_fsi/test_15.xyz \
  --output=eval.xyz --default_dtype=float64 --device=cuda
```

## License

CC BY 4.0
