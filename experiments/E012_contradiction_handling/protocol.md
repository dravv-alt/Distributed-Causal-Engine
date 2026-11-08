# E012-R001 protocol — frozen before implementation

**Date:** 2026-11-07 (Asia/Calcutta). **Planning alignment:** XP009. **Scope:** six synthetic evidence cases; no external telemetry.

## Variables and methods

- Independent variable: ranking policy (`support_only_v1` versus `contradiction_aware_v1`).
- Inference input: case ID, candidate IDs, support-evidence references, contradiction-evidence references, and evidence provenance. No labels or expected roots.
- Evaluator-only labels: root candidate or `null` for no supported root, stored in a separate file.
- Support-only score: count of support evidence per candidate. Select only a unique positive maximum; otherwise abstain.
- Contradiction-aware score: support count minus contradiction count per candidate. Select only a unique positive maximum; otherwise abstain.
- All evidence weights are 1; random seed is `null` (deterministic).

## Measures

- Contradicted-candidate rejection: among cases with a contradicted candidate, fraction where that candidate is not selected.
- Abstention: count and fraction of all cases with no selected candidate.
- Exact root accuracy: fraction of all cases whose selected candidate exactly equals the evaluator root; `null` root is correct only when the method abstains.
- False diagnosis: non-null selected candidate that differs from evaluator root (including when evaluator root is `null`).

No numeric pass threshold was specified by the campaign. Report counts and rates descriptively; do not claim statistical generalization from six synthetic cases.

## Frozen case coverage

The six inference fixtures encode: (1) supported single candidate; (2) supported but contradicted candidate versus an uncontradicted alternative; (3) only candidate fully contradicted; (4) tied support; (5) alternative candidate wins after contradiction; (6) net-score tie after contradiction. Independent labels are prepared separately and are not supplied to inference.

## Provenance and safety

Fixtures and label file are part of this experiment, not RCAEval. The implementation is isolated in `src/dce_foundation/representation_v2/contradiction.py` and imported by the experiment runner. All commands are local, no network or remote compute. Predictions are hashed before labels are opened. Failures and exact outputs are retained.
