# E010 protocol v1 — topology plus bounded trace-time support

## Frozen sample and inputs

Use the exact nine blind case IDs and pinned RCAEval revision from `configuration.json`. Before prediction, verify the current trace hashes and E009 prediction hash against the sealed E009 preflight/seal. If any differ, stop and preserve a provenance failure; do not silently change the comparison population. Prediction inputs are only the configured trace Parquet files and sealed E009 blind predictions. Missing trace files remain cases with empty candidates and abstention.

## Temporal feature

Read only `traceID`, `spanID`, `serviceName`, `parentSpanID`, and `startTimeMillis`. Resolve a parent only when `(traceID, spanID)` is unique within the case. Exclude missing, ambiguous, self-parent, missing-service, and same-service references from cross-service timing; count each state. Preserve duplicate-span identities as ambiguous rather than choosing one.

For each resolved cross-service parent-child span pair, record raw `delta = child_start - parent_start`. Let `R = max(startTimeMillis) - min(startTimeMillis)` across valid timestamps in that case. Evaluate the fixed relative bounds `0.01R`, `0.05R`, and `0.10R` (floor to integer raw units, minimum bound 1). A timing reference supports its directed service edge if `0 <= delta <= bound`. A service's temporal-only score is the number of distinct outgoing service edges for which at least half of that edge's resolved span references support the bound. Report raw-order onset inventory by service, but never call it fault onset.

For each bound, normalize topology and temporal-only scores separately within the case using min-max scaling; a constant vector becomes all zeros. Combined score is their unweighted sum. Tie credit is uniform within equal-score groups; opaque service-name order is secondary display only. No tuning, learned weights, metric values, logs, or evaluator information are allowed.

## Controls and consistency

Topology-only scores/candidates must exactly match the sealed E009 predictions. For each case and bound, rerun temporal feature construction with trace rows reversed and require exact equality of all features and rankings. Report the fraction of resolved cross-service references satisfying each bound, and the count of cases with nonempty temporal evidence. These are ordering-consistency checks, not proof of physical delay.

## Evaluation

Persist all blind predictions, provenance and their hash seal before opening evaluator-only files. Require the independent label-blind audit to match topology scores, temporal edge support, combined scores, and reverse-order results. Then join the fixed labels by the existing exact mapping files and exact case string. Report all nine cases in the denominator, including no-trace abstentions and roots absent from candidates. Metrics: tie-aware and deterministic Top-1/Top-3, root candidate coverage, abstention, root explanation coverage, exact top-score-set accuracy, and paired localization differences versus E009 topology-only. Do not report inferential significance or confidence intervals for this selected sample.

## Acceptance and provenance

Technical validity requires unchanged E009 inputs, nine prediction rows, exact baseline reproduction, row-order invariance, exact label-free audit, prediction hash sealing before label access, and exact single-row label joins. Performance has no pass threshold; report improvement, no change, or regression without selecting the best bound. Preserve failures. Record input/code/protocol/config hashes, local environment and command. No network calls; OpenResearch is unavailable locally.
