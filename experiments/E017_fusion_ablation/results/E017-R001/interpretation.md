# E017-R001 interpretation — XP014

## Results

| Arm | Top-1 (95% Wilson CI) | Top-3 | MRR | Abstention | Explanation coverage |
|---|---:|---:|---:|---:|---:|
| Neural only | 30.3% (26.8–34.1%) | 61.5% | 0.506 | 0.0% | 68.7% |
| Symbolic only | 63.2% (59.2–66.9%) | 70.7% | 0.708 | 0.0% | 83.8% |
| Neural + topology | 66.3% (62.5–70.0%) | 92.0% | 0.797 | 16.7% | 100.0% |
| Neural + topology + temporal | 90.3% (87.7–92.4%) | 100.0% | 0.949 | 12.0% | 99.8% |
| Full fusion | 89.8% (87.2–92.0%) | 98.5% | 0.942 | 11.0% | 99.0% |

Strongest independent arm was symbolic-only. Full fusion minus that arm was +26.7 percentage points Top-1; paired bootstrap 95% percentile interval was +23.0 to +30.3 points. Neural+topology+temporal scored 90.3%, 0.5 points above full fusion (an exploratory paired bootstrap interval for full-minus-that-arm was -3.3 to +2.3 points). Among non-abstained cases, full fusion's false-diagnosis rate was 5.4%; its coverage was 89.0%. Path accuracy over all cases was 89.8% and explanation coverage was 99.0%.

Independent recomputation passed for all five arms, including Top-1/Top-3/MRR, false-diagnosis, abstention, coverage, explanation coverage, path accuracy and paired point difference.

## Limits and meaning

This generator deliberately makes synthetic neural, symbolic, graph and onset features informative about a planted root. It is one simple synthetic mechanism, and each branch's score is rank-normalized with fixed equal weights. The paired interval describes these generated cases only; it does not generalize to RCAEval or live systems. Synthetic “path accuracy” checks generated graph descendants, not causal evidence. No result demonstrates that the application currently implements these fusion arms.

The highest Top-1 estimate came from neural+topology+temporal, not full fusion. In this artificial setup, adding the symbolic-like branch slightly diluted the point estimate. This supports measuring each branch and keeping weak or redundant modalities out of a fusion by default; the behavior requires testing on aligned real evidence before an application decision.
