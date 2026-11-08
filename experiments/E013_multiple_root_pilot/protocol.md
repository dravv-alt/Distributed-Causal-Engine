# E013-R001 protocol — frozen before implementation

**Date:** 2026-11-07 (Asia/Calcutta). **Planning alignment:** XP010. **Scope:** six synthetic cases (three two-root cases, three single-root controls).

## Methods

- Inference reads candidate IDs and counts of synthetic support references only.
- `single_root_v1`: select the unique maximum support candidate if its count is positive; otherwise emit an empty set.
- `root_set_threshold_2_v1`: emit every candidate with support count greater than or equal to 2; an empty set is the abstention state.
- The threshold is fixed for this synthetic pilot and is not a tuned/validated operational threshold.
- Evaluator-only root sets are stored separately and never passed to inference.

## Metrics

- Exact root-set accuracy: predicted set equals evaluator set, including empty-set matching where applicable.
- Multi-root collapse: among evaluator cases with two roots, proportion where method emits fewer than two roots.
- Ambiguity: number of all cases with a prediction set larger than one; report separately for multi-root and single-root controls.
- Also report mean predicted set size and empty-set count to expose over/under-localization.

No numeric pass threshold was specified by the campaign. Report descriptive counts/rates only. No statistical inference is valid from six designed cases.

## Provenance

Fixtures are synthetic. The user requested that the campaign continue despite pending review gates; this additive experiment does not establish XP010 on RCAEval or a controlled service testbed. No labels, schedules, or scoring points are present in inference input. No network or remote compute is used. Random seed is null because the method is deterministic.
