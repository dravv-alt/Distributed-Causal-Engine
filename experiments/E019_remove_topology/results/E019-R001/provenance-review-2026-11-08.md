# E019-R001 provenance review — 2026-11-08

This additive review records local integrity checks and leaves existing run records unchanged.

## Integrity checks

- All 23 entries in `artifact-manifest.json` match their recorded byte counts and SHA-256 hashes.
- The prediction file matches its seal, and the saved corrected independent audit reports PASS for both arms, the topology-disabled feature path, and reported metrics.
- The first audit attempt is preserved. It stopped when its comparator tried to subtract two `null` path-accuracy values for the arm that intentionally emits no explanation; the attempt note correctly classifies this as an audit-script defect.

## Reproducibility and data boundary

The manifest records file hashes but not the Git commit or dirty-tree state at execution. Experiment files are currently untracked, so a Git-frozen pre-run snapshot cannot be verified from the repository. The generated inputs, evaluator labels, and predictions remain local and are not staged for push.

## Interpretation boundary

The observed -18.7 percentage-point Top-1 change when removing topology is specific to a generator that makes the planted root the origin of a spanning directed graph. This demonstrates the designed topology cue's effect in the synthetic method, not topology's value for RCAEval or real DCE diagnosis. The existing synthetic-only interpretation remains unchanged.
