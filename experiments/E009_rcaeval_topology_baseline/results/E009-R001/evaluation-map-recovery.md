# E009-R001 evaluator mapping recovery

The first evaluator attempt stopped before reading the root-cause index because `sample-selection-2026-11-07.json` contains blind cases 0002–0009 but not the separately selected `RE2-TT-case-0001`. That failure is preserved in `evaluation-attempt-001-failure.json`.

After the prediction file was sealed and the independent blind graph audit passed, the exact one-case mapping was found in the pre-existing evaluator-only `selection-manifest.json` (`selected_case_blind_id` and `selected_case_name`). The corrected evaluator combines that existing mapping with the eight-case sample map. It does not change the population, predictions, scoring rules, or case-selection procedure. The retry is recorded in `evaluation-attempt-002.json`; hashes for the corrected evaluator and label sources are in `post-prediction-source-manifest.json`.
