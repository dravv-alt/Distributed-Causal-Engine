# E029-R001 provenance review — 2026-11-08

This additive review leaves the existing protocol, run artifacts, decision, and register unchanged.

## Integrity checks performed

- Recomputed all 20 entries in `artifact-manifest.json`; all listed files exist and match recorded sizes and SHA-256 hashes.
- Recomputed the sealed hashes for `recommendations.json` and `fixtures/inputs.json`; both match `prediction-seal.json`.
- `prediction-seal.json` records that evaluator labels were not loaded and no actions were executed. It does not include an oracle hash; the manifest's oracle-fixture hash matches the hash recorded in `independent-audit.json`.
- The stored audit reports PASS. Inspection of its source shows it checks the fixed mapping, compares recommendations with the evaluator-only oracle, and recomputes counts. It uses the same frozen action map and synthetic oracle, so it does not independently validate real action quality.

## Result and limits

The stored result reports 600 synthetic cases: 540 covered recommendations and 60 unknown diagnoses. The fixed map matched its declared mapping on all 540 covered cases; 420/540 matched the hidden synthetic oracle (77.8%). All 60 unknown diagnoses abstained, with zero recommendations. The 120 incorrect diagnoses produced visible downstream recommendation errors.

This tests error propagation and abstention in a fixed synthetic mapping. It does not evaluate DCE diagnoses, real mechanisms, real action suitability, action execution, or safety. The oracle is a generated evaluator fixture, not an independently reviewed operational policy.

## Provenance and governance discrepancy

Artifact hashes are internally consistent. The run records do not establish a frozen Git revision/clean source tree at execution, so that provenance remains unknown.

The E029 dated amendment allocates XP026 to E029, while the permanent index remains unchanged and the XP026 stage card reports the permanent experiment unallocated and the stage planned/not authorized. This review preserves the conflict; it does not make E029 canonical in the permanent index or authorize a successor stage.

## Bounded disposition

The stored synthetic mapping result and its limits are supported by the checked artifacts. Any interpretation beyond that scope remains UNKNOWN. The stored recommendation to proceed to XP027 is not itself a reviewed gate decision.
