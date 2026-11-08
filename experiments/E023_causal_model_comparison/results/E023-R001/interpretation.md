# E023-R001 interpretation — XP020

| Model | Causal-link/path accuracy (95% Wilson CI) | Sensitivity | Specificity | False-causal rate on no-effect cases | Effect RMSE vs matched intervention reference |
|---|---:|---:|---:|---:|---:|
| Observational OLS | 50.0% (46.0–54.0%) | 100% | 0% | 100% | 0.548 |
| OLS adjusted for measured U | 100.0% (99.4–100.0%) | 100% | 100% | 0% | 0.125 |
| OLS with U omitted | 50.0% (46.0–54.0%) | 100% | 0% | 100% | 0.548 |

Omitting U changed the causal-link classification for 300 of 600 cases and changed the estimated coefficient by mean absolute 0.413. The independent audit recomputed all regression coefficients, effect errors, decisions, and confusion metrics. Wilson interval bounds were clamped to [0,1].

## Assumptions and limits

The generated SCMs are linear and additive. U is observed without error and is the full common-cause adjustment set. The generated intervention contexts directly expose paired potential outcomes, which a real unit cannot simultaneously reveal. Noise, assignment, consistency, and no-interference assumptions are known by construction here. This does not identify a real causal model or establish any application path.
