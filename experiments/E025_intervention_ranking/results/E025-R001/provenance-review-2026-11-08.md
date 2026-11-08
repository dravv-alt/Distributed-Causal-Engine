# E025-R001 provenance review — 2026-11-08

This additive review records local integrity checks and leaves the original run and decision unchanged.

## Integrity checks

- All 21 artifact-manifest entries match their recorded byte counts and SHA-256 hashes.
- The prediction file matches its seal.
- The saved independent audit reports PASS for all 600 predicted action scores, best-action choices, pairwise rankings, and outcome comparisons.

## Reproducibility and data boundary

The manifest records file hashes but no Git commit or dirty-tree state. Experiment sources are currently untracked, so a Git-frozen pre-run snapshot cannot be verified from the repository. Generated indicators, evaluator-only outcomes, and predictions remain local and are not staged for push.

## Action interpretation boundary

The 99.7% best-action match is expected because the simulator makes the matching mechanism indicator informative and assigns the matching action higher expected recovery. It is a decision-pipeline check over generated data; no database repair, service scaling, or rerouting was executed. It supports no real remediation recommendation, causal effect, or safety claim.
