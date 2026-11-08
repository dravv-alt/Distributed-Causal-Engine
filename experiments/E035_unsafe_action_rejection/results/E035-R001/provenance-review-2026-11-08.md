# E035-R001 provenance review — 2026-11-08

This additive review leaves the frozen experiment files and prior results unchanged.

## Integrity and data separation

- Recomputed the 15 entries in the run manifest using its experiment-folder-relative paths; every file exists and matches its recorded size and SHA-256 hash.
- The checker reads `fixtures/proposals.json` and emits predictions. Evaluation labels are stored separately in `evaluator/labels.json`; the checker source does not load them.
- The stored independent audit reports PASS and contains a separate threshold implementation. It uses the same proposal/constraint fixtures and labels, so it cross-checks fixture/checker agreement rather than validating real service safety.

## Result and limits

The stored metrics report 500 deterministic proposals: 400/400 generated invalid cases rejected, 0 unsafe accepts, and 100/100 generated valid cases accepted. The protocol specified no acceptance threshold, so this remains descriptive rather than a pass/fail result.

The fixtures use clear-cut hand-set values for availability, replica count, and risk. No malformed/adversarial inputs, DCE integration, real service state, action execution, or collateral effects were tested. Collateral effects are not measured, not zero.

## Provenance and governance discrepancy

Manifest hashes match. A frozen Git revision/clean source snapshot at execution is not recorded; that provenance remains unknown.

The additive E035 record maps XP032 to E035, but the permanent experiment index is unchanged. The result does not authorize implementation or execution of a real remediation system.

## Bounded disposition

The small offline checker matched the simple synthetic oracle. This does not establish DCE integration, runtime enforcement, or operational safety.
