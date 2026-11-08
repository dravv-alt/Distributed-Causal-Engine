# E014-R001 provenance and audit review — 2026-11-08

This additive review records checks of the retained E014-R001 artifacts. It does not change the run outputs or the proposed decision.

## Integrity checks

- All 21 entries in the run artifact manifest exist and match their recorded byte counts and SHA-256 hashes.
- All 9 inference-input hashes, 3 evaluator-file hashes, and 11 source-file hashes in `provenance.json` match the current local files.
- The prediction file matches its seal.
- The first independent audit reports `FAIL` because its structural projection omitted `indexed_fault_rows_total` and used a different alignment key. The preserved attempt note identifies that script mismatch. The separately named `independent-audit-v2.json` reports `PASS`; its saved output and script recompute aggregate and per-case metrics, evaluator alignment, index hash, and prediction seal from predictions and local evaluator inputs.

## Reproducibility boundary

The provenance file records content hashes and environment versions but no Git commit or dirty-tree state. The experiment sources are currently untracked. Therefore a Git-frozen pre-run snapshot cannot be verified from the retained record. The runner also used per-case seeds 17 through 25, while the protocol names seed 17; this is already documented in `protocol-deviation-001.md` and is not corrected retroactively.

## Interpretation boundary

This is a within-case chronological pilot on nine selected RCAEval cases, not held-out-incident evaluation. The scored suffix is 93.0% faulty, and the autoencoder's 34.6% false-positive rate coexists with 8/8 fault-case detection. Metric meanings remain unqualified. The result is descriptive only; the existing `REVISE` proposal and pending human review remain in force.
