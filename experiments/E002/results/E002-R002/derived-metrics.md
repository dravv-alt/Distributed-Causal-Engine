# E002-R002 derived metrics

## What this run answers

E002 asks whether the provenance-aware mixed policy improves root-cause ranking over a same-source-only policy in the already frozen synthetic timing/onset experiment. R002 repeats that exact experiment after qualifying the Python environment. It does not change the question, seeds, simulator, policies, metric, or decision gate.

## Predefined gates

| Gate | Result | Evidence |
|---|---|---|
| Environment qualification | PASS | Preflight and postflight both passed: Python 3.12.6, all locked package versions, no configured thread overrides, and no import warnings. |
| Exact repeatability | PASS | Three complete repetitions produced the same canonical metrics hash: `75dac86f78573fac799f0e90103ba2501bf44e6863afe47d7f7117f7bc5f5c58`. |
| Treatment integrity | PASS | The mixed policy used 306 cross-source timing pairs. The same-source-only policy used 0. Candidate detection and thresholds were not changed. |
| Superiority | FAIL | Same-source-only minus mixed Top-1 = `0.000`; 95% paired bootstrap CI `[0.000, 0.000]`; 237 held-out events. The preregistered +0.050 requirement is not met. |

The runner's `overall_gate: true` means only that its mechanical repeatability and treatment-integrity conditions passed. It is **not** a superiority claim.

## Held-out performance

| Seed | Events | Mixed Top-1 | Same-source Top-1 | Timing-disabled Top-1 | Same-source minus mixed |
|---:|---:|---:|---:|---:|---:|
| 31 | 53 | 0.849 | 0.849 | 0.792 | 0.000 |
| 32 | 41 | 0.902 | 0.902 | 0.902 | 0.000 |
| 33 | 54 | 0.815 | 0.815 | 0.815 | 0.000 |
| 34 | 44 | 0.841 | 0.841 | 0.864 | 0.000 |
| 35 | 45 | 0.956 | 0.956 | 0.978 | 0.000 |

Every listed treatment had event recall `1.0`, incident precision `1.0`, and zero false positives in this simulator. That is an observation about this controlled synthetic regime, not an operational reliability claim.

## Plain-language interpretation

The system behaved consistently: we ran the same setup three times and received the same answer. The provenance rule also really changed which timing relationships were available to the model. But for these generated incidents, removing the cross-source relationships did not change a single final Top-1 decision. Therefore R002 strengthens confidence in the **repeatability** of E002-R001; it does not show the hybrid/provenance-aware method is better.

