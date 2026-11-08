# E017-R001 provenance review — 2026-11-08

This additive review records read-only checks and leaves the original protocol, outputs, interpretation, and decision unchanged.

## Integrity checks

- All 21 files listed in `artifact-manifest.json` exist and match the recorded byte counts and SHA-256 hashes.
- The 600-case prediction file matches `prediction-seal.json`; its seal records `labels_loaded: false` and `network_used: false`.
- The saved independent audit reports PASS after recomputing metrics for all five arms, coverage, explanation paths, and the paired comparison.

## Reproducibility and data boundary

The manifest records content hashes but not a Git commit or dirty-tree state. The experiment sources are currently untracked, so the record does not establish a Git-frozen pre-run snapshot. Generated inputs, evaluator labels, and predictions remain local and are not staged for push.

## Interpretation boundary

The +26.7 percentage-point full-fusion difference over the strongest independent arm is specific to one designed synthetic generator. The neural+topology+temporal arm scored 0.5 points higher than full fusion; the exploratory paired interval spans zero. Generated path correctness is not causal evidence. No RCAEval or application-level fusion claim follows, and the existing synthetic-only disposition remains unchanged.
