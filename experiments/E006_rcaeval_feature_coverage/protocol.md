# E006 protocol v1 — sampled feature coverage audit

## Scope and separation

Read only the nine blind `field-audit.json` files under `data/rcaeval/inference/`. The audit must reject unexpected case IDs, a revision mismatch, any input that says labels were loaded, or a missing audit file. Do not read evaluator-only files, case names, labels, injection schedules, fault files, or raw ground truth. Do not modify inference data or prior run records.

## Fixed sample and measures

The fixed blind IDs are `RE2-TT-case-0001` and `blind-case-0002` through `blind-case-0009`; together they represent nine source groups per the existing local selection manifest. For each, report metric rows, timestamp field, metric feature count (excluding `time`), per-feature dtype/non-null/null counts, missing cells, log/trace availability and row counts, and the source audit's exact metric/log timestamp intersection counts. Report the union and intersection of metric feature names across all nine.

Reference is the saved per-case field catalog, which was produced directly from the pinned Parquet cases. The script verifies the catalog and reports it; it does not infer feature meaning or repair missing values. Exact integer timestamp intersection is a descriptive join only.

## Analysis and stop conditions

Summarize ranges and per-case values descriptively. Do not compute or claim population estimates, confidence intervals, detector quality, feature importance, complete alignment, or causal effects. Missing modalities are `UNKNOWN`/unavailable for that sample, not evidence of system-wide absence. Treat every non-time column's source semantics as `UNKNOWN` absent independent documentation.

Stop with a failed run if an expected input is missing, malformed, label-bearing, revision-inconsistent, or fails the basic row/column conservation checks. Preserve the failure in the new run directory. Never overwrite a result directory.

## Provenance

Record Git HEAD and dirty status, Python version, ORX availability, configuration/protocol/runner hashes, all input audit hashes, and the exact command. The execution is offline/local and consumes only local audit JSON files. OpenResearch is not available; do not describe the run as OpenResearch-managed.
