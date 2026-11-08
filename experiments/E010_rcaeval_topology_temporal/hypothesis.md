# E010 preregistered question and hypothesis

**Question:** Does adding parent-before-child span timing evidence to E009's topology-only shared-caller ranking change exact-service localization on the same nine selected RCAEval cases, and are the resulting scores invariant to trace-row ordering?

**Hypothesis:** A temporal support feature based on bounded parent-to-child raw timestamp differences may change the ranking and will be deterministic under row-order permutation. Any localization gain or loss is descriptive only because the feature is not a verified fault-onset or latency signal.

**Independent variables:** topology-only baseline; temporal-only support rank; equal min-max normalized topology-plus-temporal rank at relative bounds of 1%, 5%, and 10% of each case's raw trace timestamp range.

**Dependent measures:** tie-aware and deterministic Top-1/Top-3 localization; root candidate coverage; abstention; localization delta from the frozen topology baseline; parent-child temporal support fraction; rank/input-order consistency; onset-order inventory.

**Inputs:** The nine fixed blind IDs from E009. Inference may read only each case's `traces.parquet` and the hash-sealed E009 `predictions.jsonl` plus its seal. It may not read metrics, logs, `field-audit.json`, evaluator maps, labels, injection times, or fault fields. The evaluator opens label data only after predictions are sealed and an independent label-blind audit passes.

**Baseline:** the original, hash-sealed E009 topology-only predictions for identical blind cases and unchanged trace hashes. Also report the E009 graph-disabled uniform result for context.

**Temporal semantics:** use `startTimeMillis` only as a numeric ordering field. Do not infer milliseconds, timezone, clock synchronization, causal delay, anomaly onset, or service health from its name or magnitude. For each resolved cross-service parent-child span pair compute `raw_delta = child_start - parent_start`; an edge reference supports a bound only when `0 <= raw_delta <= bound_fraction * per-case(raw_max - raw_min)`. Report all fixed fractions; do not choose one post hoc. Service onset means earliest observed span timestamp in this file, not failure onset.

**Limits:** the nine cases are deliberately selected, not a probability sample. Trace volume and span ordering are instrumentation-dependent. The result is not held-out, online, causal, or production evaluation and does not test neural-symbolic effectiveness.
