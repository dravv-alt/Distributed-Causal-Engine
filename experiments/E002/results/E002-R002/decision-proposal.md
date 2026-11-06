# E002-R002 decision proposal

**Review status:** pending human review. This is a new R002 artifact. E002-R001 has not been edited.

## Proposed decision: REVISE

The R001 environment-record issue is resolved for this rerun: the qualified R002 interpreter passed preflight and postflight verification with the frozen Python/package versions and no runtime import warnings. The repository test suite also passed (`49 passed`).

R002 exactly reproduces R001's raw results under that environment. It passes the predefined repeatability and treatment-integrity gates, but fails the predefined superiority gate: the paired Top-1 difference remains `0.000` with a 95% CI of `[0.000, 0.000]` across 237 events. No claim that the hybrid/provenance-aware policy outperforms the simpler policy is justified.

## What is now established

- This frozen synthetic E002 calculation is repeatable on the qualified current host.
- The source-policy switch changes cross-source timing-pair use as designed.
- R001's observed null performance difference was not caused by the previously recorded incompatible dependency combination.

## What is not established

- Hybrid superiority.
- Performance on real distributed telemetry or OpenRCA.
- Deployment readiness, causal correctness, or remediation ability.
- Portable clean-room reconstruction from downloaded, hash-pinned package wheels; this host had to use verified locally available packages after package-index DNS failure.

**Required next action:** human review of this decision proposal. Stop here; do not start E003 remediation, RCAEval work, or new reasoning work automatically.

