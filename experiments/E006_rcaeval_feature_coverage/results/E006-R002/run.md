# E006-R002 run record — complete local inference-file scan

Date: 2026-11-08  
Planning stage: XP003.  
Mode: standalone local scan; `orx` unavailable; not OpenResearch-managed.  
Protocol: additive [R002 amendment](../../protocol-amendment-r002.md); E006-R001 remains unchanged.

## Scope and execution

The run read every direct metric/trace/log Parquet file in the nine frozen blind-case inference directories. It scanned 19 local files and 833,551 rows total: 9,886 metric rows, 345,991 log rows, and 477,674 trace rows. It did not open the evaluator-only directory, labels, fault names, or injection schedules. The runner used local PyArrow; network and remote compute were not used.

The raw scan found metrics for 9/9 cases, logs for 6/9, and traces for 4/9. Metric feature names had a union of 560 and an intersection of zero across the nine cases. The metric tables contained 53,359 top-level null feature cells out of 1,619,099 feature cells (3.30%). These counts describe only the selected local files.

Timestamp-like field names differed across modalities (`time`, `timestamp`, `startTimeMillis`, and `startTime`). The frozen exact-same-name-and-type overlap check found zero comparable cross-modal field pairs. This does not prove timestamps are unrelated or aligned; units, timezone, clock relation, temporality, and event meaning remain UNKNOWN.

The independent read-only audit recomputed all 19 input hashes, rows, schemas, and top-level null counts; it passed all 13 checks. Machine output is in `feature-scan.json`, provenance in `source-manifest-r002.json`, and the recomputation in `independent-audit-r002.json`.

The Python process emitted optional pandas warnings about local `numexpr` and `bottleneck` versions while importing PyArrow. The scan completed successfully; no pandas computation was used by this runner.

## Evidence boundary

RCAEval's pinned index contains 735 cases, but the local inference telemetry scan covers only the nine frozen sample cases. No claim is made about the remaining 726 cases or the complete telemetry corpus. The scan verifies file and field presence, not metric semantics, units, temporal validity, aligned-window coverage, feature-extractor behavior, or RCA quality. A zero all-case feature intersection means these nine schemas share no exact non-time feature column; it is not evidence that no useful normalization or mapping can exist.

## Artifacts

- `feature-scan.json`: per-file schemas, hashes, row counts, top-level null counts, feature coverage, timestamp candidate summaries, and exact raw overlap results
- `source-manifest-r002.json`: local environment and source/input hashes
- `independent-audit-r002.json`: separate recomputation audit
- `artifact-manifest-r002.json`: output and source fingerprints
- scripts: `run_local_corpus_r002.py`, `audit_local_corpus_r002.py`, and `create_artifact_manifest_r002.py`
