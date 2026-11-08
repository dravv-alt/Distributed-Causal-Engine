# E018-R001 provenance review — 2026-11-08

This additive review records read-only integrity checks. It does not change the original run or proposed decision.

## Integrity checks

- All 22 files listed in `artifact-manifest.json` exist and match their recorded byte counts and SHA-256 hashes.
- The prediction file matches its seal.
- The saved independent audit reports PASS after reconstructing all 600 neural-disabled score vectors without using the neural feature, and recomputing both arms' metrics and diagnostics.

## Reproducibility and data boundary

The retained manifest records content hashes but no Git commit or dirty-tree state. The experiment sources are currently untracked, so a Git-frozen pre-run snapshot cannot be established from the repository. Generated inputs, evaluator labels, and predictions remain local and are not staged for push.

## Interpretation boundary

On this fresh sample from the E017 synthetic generator, removing the neural-like modality changed Top-1 by +1.3 percentage points, with a paired 95% interval from -1.5 to +4.0. The interval includes no effect. The fixed-temperature softmax rank diagnostics are not calibrated probabilities. No application, RCAEval, or real-system neural contribution is established; the existing inconclusive disposition remains in force.
