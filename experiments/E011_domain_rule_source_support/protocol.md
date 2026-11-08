# E011-R001 protocol — frozen before execution

**Date:** 2026-11-07 (Asia/Calcutta)  
**Scope:** local, exploratory, label-blind source-support inventory for the XP008 illustrative rule.  
**Permanent ID:** E011.  
**Planning alignment:** XP008; no pass claim.

## Inputs

The exact nine blind inference directories selected for E010: `RE2-TT-case-0001` and `blind-case-0002` through `blind-case-0009`. Read `metrics.parquet`, `logs.parquet`, `traces.parquet`, and `field-audit.json` when present. Read `src/dce_foundation/domain.py` as the current domain contract. Exclude `data/rcaeval/evaluator-only/` entirely.

## Procedure

For each file, record its relative path, byte size, and SHA-256 before and after scanning. Inspect Parquet column names and aggregate row counts. Search log message text in memory for case-insensitive literal terms `database`, `db`, `pool`, `saturat`, `overload`, `exhaust`, `latency`, and `service`; save only aggregate counts, never message text. Record field-name matches separately from message-text matches.

The illustrative candidate rule is interpreted as three literal predicate families: (1) database saturation/overload, (2) connection-pool saturation/exhaustion, and (3) latency. These are lexical probes only. No undocumented metric meaning, entity identity, threshold, event timing, or causal relation is inferred.

## Outputs and analysis

Write `results/E011-R001/source-support.json` with case/modalities/rows/columns, token counts, file hashes, source hash, environment, and explicit limitations. A second script run is not part of this run. Metrics are availability counts only; localization delta and rule/path accuracy are explicitly not estimable by this protocol.

## Reproducibility and safety

Python/Polars versions are recorded. Random seed is `null` because the procedure is deterministic. Network access is disabled by design (no networking code). No external compute is used. The source tree is unchanged by execution.
