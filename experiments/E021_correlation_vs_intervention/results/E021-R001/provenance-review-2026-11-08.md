# E021-R001 provenance review — 2026-11-08

This additive review records local artifact checks. It does not change the existing run or decision.

## Integrity checks

- All 21 artifact-manifest entries exist and match their recorded byte counts and SHA-256 hashes.
- The prediction file matches its seal; the seal records that evaluator labels were not loaded and no network was used.
- The saved independent audit reports PASS after recomputing all 600 observational/intervention estimates and both decision rules.

## Reproducibility and data boundary

The manifest records content hashes but not a Git commit or dirty-tree state. The source files are currently untracked, so a Git-frozen pre-run snapshot cannot be verified from the retained evidence. The generated values, paired outcomes, evaluator mechanism labels, and predictions remain local and are not staged for push.

## Causal interpretation boundary

The 100% intervention-rule result is expected under these generated structural equations: the simulator constructs matched potential outcomes and inserts a 1.3 effect for the direct-cause class while omitting the treatment effect for the common-cause class. This validates the rule on the declared simulation, not a causal effect or causal edge in DCE, RCAEval, or a real service. A real intervention observes only one potential outcome per unit and needs its own design assumptions and controls.
