# E027-R001 provenance review — 2026-11-08

This additive review records read-only checks and does not change the existing run or disposition.

## Integrity checks

- All 20 artifact-manifest entries match their recorded byte counts and SHA-256 hashes.
- `plans.json` matches its seal.
- The saved independent audit reports PASS after recomputing plan validity, healthy-replica availability, disruption, budget, rejection, and goal attainment across 400 cases.

## Reproducibility and data boundary

The manifest records content hashes but no Git commit or dirty-tree state. Experiment sources are currently untracked, so the repository cannot verify a Git-frozen pre-run snapshot. Synthetic states, evaluator-only feasibility labels, and plans remain local and are not staged for push. No plan was executed.

## Safety interpretation boundary

The constrained planner satisfied the declared toy contract: 220 accepted plans were valid and 180 infeasible cases were rejected, with zero false acceptances in these generated cases. This does not establish runtime enforcement, race resistance, complete production constraints, or safe real remediation. The existing decision remains offline synthetic validation only.
