# E011 execution ledger

## E011-R001 — initial substring scan

Executed `python experiments/E011_domain_rule_source_support/scripts/run_audit.py` locally against the nine frozen blind inference cases. The scan retained input hashes and aggregate outputs in `results/E011-R001/source-support.json`. Substring matching inflated counts (`db` can occur inside unrelated strings); this attempt is preserved and excluded from the corrected predicate assessment.

## E011-R002 — token-boundary scan

Executed `python experiments/E011_domain_rule_source_support/scripts/run_audit_r002.py` after freezing `protocol-amendment-R002.md` and its separate runner. The run read only the nine `data/rcaeval/inference/` directories and `src/dce_foundation/domain.py`; it did not open evaluator-only files. It reported per-input SHA-256 values, verified each Parquet file was unchanged during its scan, and wrote `results/E011-R002/source-support.json`.

Observed aggregate counts: 9,886 metric rows, 345,991 log rows, 477,674 trace rows; 238 metric field names contain the token `latency`; metric field names contain the token `db` 50 times across cases (20 distinct field names); 13 log messages contain `database`, 33 contain the standalone token `db`, and 2,019 contain `pool`. There were zero log messages containing database plus saturation/overload terms and zero containing pool plus saturation/exhaustion terms. No saturation, overload, exhaustion, or latency token occurred in log text.

These counts describe strings only. `db` component names and latency suffixes do not qualify metric meaning, units, healthy ranges, entity linkage, time semantics, or fault state. The run cannot compute localization delta or rule/path accuracy. It is not a held-out or confirmatory XP008 comparison.
