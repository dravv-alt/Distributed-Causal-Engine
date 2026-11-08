# E009-R001 result interpretation

## Observed metrics

All nine frozen cases remain in the denominator. The topology method had five abstentions because those cases had no trace file. The matched graph-disabled uniform baseline also abstained on those same five cases.

| Method | Top-1 tie-aware | Top-3 tie-aware | Top-1 lexical | Top-3 lexical | Root candidate coverage | Abstentions | Root explanation coverage |
|---|---:|---:|---:|---:|---:|---:|---:|
| Topology shared callers | 0.0% | 7.4% | 0.0% | 11.1% | 44.4% (4/9) | 5/9 | 33.3% (3/9) |
| Graph-disabled uniform | 4.3% | 12.9% | 11.1% | 22.2% | 44.4% (4/9) | 5/9 | 0.0% |

The topology-minus-uniform tie-aware differences are **−4.3 percentage points Top-1** and **−5.4 points Top-3**. Exact top-score-set accuracy was 0/9 for both methods. An independent evaluator-side audit recomputed the metrics and matched `evaluation.json`.

## Interpretation and limits

This topology heuristic did not outperform the matched uniform reference on the nine selected cases. The sample was chosen for data coverage, is not random, and is too small to support a population estimate or inferential significance. Five cases had no traces and forced abstention. The root appeared among observed service candidates in four cases. Exact service-name matching was used with no aliases.

These are retrospective exact-service localization metrics on a selected subset. They do not evaluate online detection, symptom evidence, causal reasoning, neural-symbolic fusion, or the campaign's held-out ≥5-point quality target. A trace edge is structural evidence, not proof that a service failed or caused downstream symptoms. No post-label tuning was performed.

## Leakage and execution record

The prediction process read only configured blind `traces.parquet` files. Its prediction file was sealed before any evaluator-only mapping or label-index read. A separate label-blind audit independently rebuilt edges and scores for all nine cases. The first evaluator attempt stopped before reading the label index because it used an eight-case map; the exact pre-existing single-case selection manifest was then combined with that map. The failure and recovery are recorded in `evaluation-attempt-001-failure.json`, `evaluation-map-recovery.md`, and `evaluation-attempt-002.json`. The independent metric audit's initial abstention-format defect and corrected passing retry are both retained.

All work remained local; `orx` was unavailable and no network was used. The source, dataset revision, trace hashes, prediction seal, mapping hashes, label-index hash, and result hashes are retained in the run artifacts. Human review remains pending.
