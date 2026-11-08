# E010-R001 result interpretation

## Observed localization

All nine selected cases remain in the denominator. Five cases had no traces and all methods abstained on those cases; the root appeared among observed service candidates in 4/9 cases.

| Method | Top-1 tie-aware | Top-3 tie-aware | Top-1 lexical | Top-3 lexical | Root coverage | Abstentions |
|---|---:|---:|---:|---:|---:|---:|
| E009 topology-only | 0.0% | 7.4% | 0.0% | 11.1% | 44.4% | 5/9 |
| Temporal-only (all 3 bounds) | 5.6% | 11.1% | 11.1% | 11.1% | 44.4% | 5/9 |
| Topology + temporal (all 3 bounds) | 11.1% | 11.1% | 11.1% | 11.1% | 44.4% | 5/9 |
| E009 graph-disabled uniform | 4.3% | 12.9% | 11.1% | 22.2% | 44.4% | 5/9 |

Topology-plus-temporal changed tie-aware Top-1 by **+11.1 percentage points** and Top-3 by **+3.7 points** versus E009 topology-only in this sample. It remained below the uniform reference on Top-3. These are descriptive paired sample differences, not inferential estimates. The main held-out ≥5-point Top-1 campaign target is **not evaluated** by this selected, reused sample.

## Temporal consistency and sensitivity

The label-blind audit matched predictions for all nine cases, and reversed trace-row order produced the same temporal features/rankings. Across **170,239 resolved cross-service span references**, the fraction satisfying the preregistered parent-before-child relative-delay bound was **100%** at 1%, 5%, and 10% of each case's raw timestamp range. All three bound settings produced the same reported localization metrics, so the sensitivity sweep did not distinguish cases here.

## Limits

The temporal score is a proxy: `startTimeMillis` was used only as a raw numeric ordering field. Its formal units, timezone, clock synchronization, relationship to arrival time, and connection to fault onset are unknown. The relative bounds are not physical latency limits. Trace volume and parent-child timing may reflect instrumentation behavior. The feature does not establish causal propagation or symptoms. The nine cases are selected, not random; there are no confidence intervals or significance claims. This is retrospective and not held out, online, or production evaluation.

## Provenance and review

E010 reused the exact E009 trace hashes and topology predictions, verified before inference. Predictions were sealed and independently audited before evaluator labels were opened. The independent evaluator audit reproduced all aggregate metrics and localization deltas. No network was used; `orx` was unavailable. Full hashes and outputs are in `preflight.json`, `prediction-seal.json`, `independent-audit.json`, `evaluation.json`, `independent-evaluation-audit.json`, and the artifact manifest.
