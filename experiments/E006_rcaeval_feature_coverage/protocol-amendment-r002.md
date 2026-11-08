# E006-R002 protocol amendment — complete local telemetry-file coverage

Date frozen: 2026-11-08  
Run: E006-R002, XP003, same existing E006 scope; no new permanent E ID.  
Status: additive amendment; E006-R001 and its sampled field-audit protocol remain unchanged.

## Research question

What metric, trace, and log fields, null patterns, row counts, and raw timestamp-field overlaps are present across every RCAEval inference Parquet file currently available locally for the nine frozen blind cases?

## Scope and input boundary

Read only direct Parquet files under `data/rcaeval/inference/<frozen-case-id>/` for `RE2-TT-case-0001` and `blind-case-0002` through `blind-case-0009`. Scan every locally present modality file in those nine directories; expected discovered input count at protocol freeze is 19. Do not read `data/rcaeval/evaluator-only/`, labels, fault names, descriptions, injection times, or schedules. Do not make network requests, modify data, or update E006-R001 artifacts.

This is a complete scan of the local inference files for the fixed nine-case sample, not a full scan of the 735-case RCAEval index or corpus. A missing local modality is reported as unavailable, not as zero rows or population-wide absence.

## Fixed measurements

For every Parquet file record its relative path, SHA-256, byte size, row count, ordered column names, Arrow types, and top-level null counts. For each scalar field whose name contains `time` or `timestamp` case-insensitively, record available raw min/max, distinct count, null count, duplicate count, and source-order monotonicity when its type supports those operations. Do not convert, normalize, or assign units.

For the nine metric tables, report field union/intersection, per-field case presence, per-case total feature cells/nulls, and the observed `time` column properties. Across modalities, compute exact raw value intersection only for fields with the exact same name and Arrow type and comparable scalar values. Record the paired field names and type. A raw equality count is descriptive; it does not establish common clock, timezone, unit, alignment tolerance, or event-time meaning.

For every field, measurement unit, temporality, aggregation, reset behavior, semantic meaning, and service identity remain `UNKNOWN` unless represented by independently documented source metadata. Do not infer meaning from a column name or observed numeric range.

## Analysis and failure handling

Require all nine frozen directories. Ignore all directories and files outside those nine directories without opening them. Within each frozen directory, process every direct Parquet file whose stem is one of `metrics`, `traces`, or `logs`; fail on any other direct Parquet file. Record absent expected modality files. Retain a failed run if any discovered Parquet file cannot be read or hashed. Verify that recomputed input hashes and row/column summaries match a separate read-only audit. Do not silently drop unreadable columns or cases.

No confidence interval or population estimate is computed. The results are descriptive of these nine selected cases and the local data snapshot only. This amendment does not qualify XP003's full-dataset coverage or any model/RCA performance.

## Provenance and local-only handling

Record exact run command, Git HEAD/worktree status, Python/PyArrow versions, protocol/config/runner hashes, and each input file hash. Record OpenResearch CLI availability accurately; this standalone local run is not OpenResearch-managed. Network access is disabled by design; no telemetry leaves the device.
