# E018-R001 interpretation — XP015

| Arm | Top-1 (95% Wilson CI) | Top-3 | MRR | Abstention | Coverage | Multiclass Brier* | 10-bin ECE* |
|---|---:|---:|---:|---:|---:|---:|---:|
| Full fusion | 88.7% (85.9–91.0%) | 98.3% | 0.935 | 11.5% | 88.5% | 0.207 | 0.177 |
| Neural disabled | 90.0% (87.3–92.2%) | 99.3% | 0.946 | 12.0% | 88.0% | 0.173 | 0.137 |

*Calibration diagnostics use softmax-transformed within-case rank scores at a fixed temperature of 0.1. They are not calibrated probabilities for DCE.

Paired neural-disabled minus full Top-1 was +1.3 percentage points (95% bootstrap interval -1.5 to +4.0). Paired MRR difference was +0.0108 (95% interval -0.0049 to +0.0261). The independent audit recomputed the scores and metrics, including all 600 neural-disabled score vectors without use of the neural feature.

## Limits

This reuses the E017 synthetic generator under a new seed. The generated modalities are intentionally informative, but their strength and dependence are generator choices. Rank fusion and temperature-based diagnostics are not DCE's validated neural model or probability calibration. The result neither supports nor refutes neural value on RCAEval or real workloads. The observed differences are small and uncertainty includes no effect.
