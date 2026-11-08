# E016-R001 provenance review — 2026-11-08

This additive review records local artifact checks. It does not change the protocol, outputs, interpretation, or review status.

## Integrity checks

- All 28 entries in `artifact-manifest.json` exist and match their recorded byte counts and SHA-256 hashes. This includes synthetic fixtures, trained model files, predictions, evaluation, audit, and source files.
- `predictions.json` matches the prediction seal.
- The saved independent audit reports PASS for the stated localization, membership mismatch, permutation, malformed-input, and seal checks.

## Reproducibility and data boundary

The manifest preserves content hashes but not the Git commit or dirty-tree state at execution. These source files are currently untracked, so a Git-frozen pre-run snapshot cannot be established from the repository. Synthetic fixtures, labels, weights, and predictions remain local under the repository's ignore policy and are not staged for push.

## Interpretation boundary

The results support only synthetic architecture feasibility for one generated data distribution. The generated root and descendant signals encode the answer, and the shared model's strong localization does not isolate a causal contribution from topology. It does not establish RCA quality or adaptation to real service names, schemas, graphs, or faults. The existing record correctly leaves real-service effectiveness `UNKNOWN`; human review is not recorded.
