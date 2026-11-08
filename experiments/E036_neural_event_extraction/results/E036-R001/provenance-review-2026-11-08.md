# E036-R001 provenance review — 2026-11-08

This additive review preserves the original run files and decision.

## Integrity and independent recomputation

- Recomputed all 16 artifact-manifest entries; every listed file exists and matches its recorded byte count and SHA-256 hash.
- Read the inference source: it loads synthetic training messages and their training labels, but it does not load the held-out test labels. Test labels are opened only by the separate evaluation script.
- Independently recomputed held-out accuracy, macro F1, output fields, and source-ID retention from `predictions.json` plus the evaluator-only test labels. The results match the stored 1.00 accuracy, 1.00 macro F1, schema compliance, and 150/150 source IDs.
- There is no stored independent-audit artifact; this dated review records the separate recomputation performed here.

## Result and construction limits

The synthetic classifier scored 1.00 accuracy and macro F1 on 150 held-out generated messages; the fixed keyword reference scored 0.84. The vocabulary is only 12 repeated templates across three classes, and train/test text is generated from the same template list with small metadata changes. The perfect neural score therefore demonstrates the pipeline can learn these templates, not robust event extraction.

No row-level event labels or scored real RCAEval/OpenRCA/DCE logs were used. The softmax `confidence` field is explicitly uncalibrated. Provenance retention is a fixture-field check, not validation of real source-record traceability.

## Provenance and governance discrepancy

Manifest hashes match, but a frozen Git revision/clean source snapshot at run time is not recorded; that provenance remains unknown.

The E036 amendment maps XP033 to this synthetic pilot. Real-data extraction accuracy and the planned held-out benchmark remain unestablished; no numeric acceptance threshold was approved.

## Bounded disposition

The synthetic text-training and output-schema pipeline works on its generated template distribution. Real event extraction quality remains UNKNOWN; this result is not an XP033 pass.
