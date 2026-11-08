# E009 protocol v1 — topology-only baseline on blinded RCAEval samples

## Frozen population and isolation

Use the fixed blind case IDs in `configuration.json` and the locally staged dataset revision. The prediction process may open only each configured `traces.parquet` file under `data/rcaeval/inference/<blind-id>/`. It must not open `field-audit.json`, metrics, logs, any evaluator-only file, the sample-selection manifest, or the label-bearing parquet index. A missing `traces.parquet` is represented as an empty candidate set and an explicit abstention, not an omitted case.

Write all predictions to a new `results/E009-R001/predictions.jsonl`, flush/close it, then record its SHA-256 in `prediction-seal.json`. Only after that seal exists may the separate evaluator read `data/rcaeval/evaluator-only/sample-selection-2026-11-07.json` and `index-afeacb1/cases.parquet`.

## Graph construction

From each trace file, resolve `(traceID, spanID)` identities within that case. Build a directed edge from parent service to child service only if the parent span identity resolves exactly once and both spans have nonempty service names. Do not infer service aliases or edges from unresolved references, null parents, self-parents, or same-service spans. Deduplicate parallel service edges for ranking while preserving their span-reference counts for explanation. Keep isolated observed service names as candidates. Report duplicate span IDs and unresolved/ambiguous parent counts; they are not silently repaired.

## Frozen ranking and references

- `topology_shared_callers_v1`: each observed service score is the number of distinct other observed services that can reach it along the directed caller-to-callee graph. Reachability uses a visited set and terminates under cycles. Scores are structural ranks, not probabilities or fault evidence. Ties receive uniform expected Top-k credit; opaque service-name order is secondary display only.
- `graph_disabled_uniform_v1`: score all observed services equally, independently of graph inputs. It is the matched chance reference. When the candidate set is empty, both methods abstain.

The reasoner emits service candidates, integer scores, reachable-caller evidence and span-reference counts. It never emits fault labels or claims that the candidate is faulty.

## Evaluator and metrics

After sealing predictions, map each blind ID to the source case name through the evaluator-only sample map, then join by exact `case` string in the label-bearing index. Require exactly one row per selected case. Exact root-service string equality determines coverage; do not fuzzy-match. Keep all nine cases in the denominator, including no-trace, root-absent, and abstaining cases. Report per-case and aggregate tie-aware Top-1/Top-3, deterministic lexical secondary Top-1/Top-3, root candidate coverage, abstentions, explanation coverage, and paired case-level differences. Report no significance claim or confidence interval because this small selected set is not a probability sample and cases are not established independent.

## Acceptance and failure handling

Technical integrity checks require nine prediction rows, no label-bearing input access by prediction code, exact prediction hash seal before evaluator access, all predictions reproducible from the same trace files, exact single-row evaluator joins, and independent recomputation of rank scores/metrics. A failure in integrity or leakage checks invalidates scoring; preserve outputs and report failure. Model performance has no threshold in this descriptive stage. Do not tune method rules or choose a better subset after viewing labels.

## Provenance and boundary

Record input trace hashes, pinned dataset revision, code/config/protocol hashes, Git state, Python/Polars/NetworkX versions, hardware where queryable, exact command, and complete outputs. All input files and results remain local; make no network calls. `orx` is unavailable, so this run is standalone and must not be represented as OpenResearch-managed.
