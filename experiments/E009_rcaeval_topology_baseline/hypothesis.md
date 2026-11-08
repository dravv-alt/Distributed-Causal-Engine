# E009 preregistered question and hypothesis

**Question:** On the nine fixed blind RCAEval sample cases, how often does a trace-topology-only shared-dependency ranking place the exact evaluator root-cause service in Top-1 or Top-3, compared with a graph-disabled uniform ranking on the same observed-service candidate universe?

**Hypothesis:** Service-call structure may provide localization information beyond a graph-disabled uniform reference, but performance is not assumed. Missing/ambiguous trace context may force abstention or reduce candidate coverage.

**Independent variables:** graph-derived shared-caller ranking versus graph-disabled uniform ranking; trace availability/parent resolution.

**Dependent measures:** exact root Top-1 and tie-aware Top-3 credit; root candidate coverage; abstention; explanation coverage; parent resolution states; candidate count; paired per-case score differences.

**Prediction inputs:** only `traces.parquet` from the configured blind inference directories. Use all trace rows in each file. The reasoner receives no evaluator labels, injection times, case names, selection mapping, metrics, or logs. The evaluator later uses exact case mapping and exact root-service string matching; no fuzzy alias matching.

**Baseline/reference:** `graph_disabled_uniform_v1`, assigning every observed service equal score; it receives the same trace-derived candidate set. Cases with no traces have an empty set and both methods abstain.

**Scope and limits:** The nine cases were selected by a prior label-blind smallest-payload rule, not randomly. Only trace-present cases can form topology edges. This descriptive sample does not support population estimates, inferential significance, online detection, causal claims, or neuro-symbolic effectiveness. The source case index is evaluator-only and remains unopened until predictions are persisted and hashed.
