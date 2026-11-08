# E021-R001 interpretation — XP018

| Rule | Sensitivity (95% Wilson CI) | Specificity (95% Wilson CI) | Balanced accuracy | False-causal rate on common-cause cases |
|---|---:|---:|---:|---:|
| Observational correlation | 60.3% (54.7–65.7%) | 44.7% (39.1–50.3%) | 52.5% | 55.3% |
| Matched intervention effect | 100.0% (98.7–100.0%) | 100.0% (98.7–100.0%) | 100.0% | 0.0% |

The intervention classifier uses a fixed 0.50 mean-effect threshold; the correlation classifier uses an absolute 0.50 Pearson threshold. Both were applied to the same 600 cases, with 300 examples of each mechanism. The audit independently recalculated all observational correlations, matched differences, and confusion counts.

## Assumptions and limits

This is a simulation with known structural equations. The matched `do(A=0)` and `do(A=1)` potential outcomes share a generated context by construction. Real experiments do not usually observe both potential outcomes for the same unit; their interpretation needs a sound intervention design and assumptions about consistency, interference, measurement, and population. The result establishes no causal edge or intervention effect in DCE, RCAEval, or any operating service.
