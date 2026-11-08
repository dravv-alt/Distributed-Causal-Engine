# E024-R001 provenance review — 2026-11-08

This additive review records local artifact checks and leaves the original run and proposed decision unchanged.

## Integrity checks

- All 24 artifact-manifest entries match their recorded byte counts and SHA-256 hashes.
- The prediction file matches its seal.
- The saved independent audit reports PASS after independently refitting training OLS and recomputing all 400 held-out predictions and baseline comparisons.

## Reproducibility and data boundary

The manifest records content hashes but not a Git commit or dirty-tree state. Experiment sources are currently untracked, so a Git-frozen pre-run snapshot cannot be verified from the repository. Synthetic training data, held-out contexts, matched intervention outcomes, and predictions remain local and are not staged for push.

## Counterfactual interpretation boundary

The model improved over a no-change baseline in a simulator where the linear mechanism, fully measured confounder, noise law, and paired potential outcomes are known and shared between training and testing. This supports the expected behavior under those assumptions only. It does not validate counterfactual prediction for DCE or real services.
