# E020-R001 provenance review — 2026-11-08

This additive review records read-only checks and does not alter the original run or proposed decision.

## Integrity checks

- All 22 entries in `artifact-manifest.json` exist and match their recorded byte counts and SHA-256 hashes.
- The prediction file matches its seal.
- The saved independent audit reports PASS for the temporal-disabled score path, evaluator-only onset consistency, both arms' metrics, and label separation.

## Reproducibility and data boundary

The artifact manifest preserves file hashes but no Git commit or dirty-tree state. Experiment files are currently untracked, so a Git-frozen pre-run snapshot cannot be established from the repository. Generated fixtures, labels, and predictions remain local and are not staged for push.

## Interpretation boundary

The -13.0 percentage-point Top-1 change on removing temporal input is specific to generated onset values intentionally associated with planted roots. The synthetic timestamps have no units or real event-time, clock-skew, reset, or late-arrival semantics. This does not qualify temporal evidence on RCAEval or application telemetry; preserve the existing synthetic-only disposition.
