# E023-R001 provenance review — 2026-11-08

This additive review records read-only checks and does not change the original experiment records.

## Integrity checks

- All 21 artifact-manifest entries match their recorded byte counts and SHA-256 hashes.
- The prediction file matches its seal.
- The saved independent audit reports PASS after recomputing all 600 OLS estimates, intervention-reference errors, link decisions, and confounder sensitivity.

## Reproducibility and data boundary

The manifest preserves content hashes but no Git commit or dirty-tree state. The experiment sources are currently untracked, so the repository cannot verify a Git-frozen pre-run snapshot. Generated observations, paired potential-outcome references, evaluator labels, and predictions remain local and are not staged for push.

## Causal interpretation boundary

The adjusted model's perfect link classification follows from the simulator's linear equations, an exactly observed common cause, and matched potential outcomes. The result demonstrates the expected behavior under those known assumptions; it does not establish that the adjustment set or structural model is correct for DCE or any real system. Real-world causal identification remains untested.
