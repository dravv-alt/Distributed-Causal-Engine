# E017-R001 protocol — frozen before implementation

Date: 2026-11-07 (Asia/Calcutta). Alignment: XP014. Scope is a deterministic synthetic pilot; RCAEval inputs and labels are not used.

## Dataset and split

- Generate 600 held-out cases; each case has 10 services, one synthetic root, a directed graph, a neural-like local score, a symbolic-like rule score, and a temporal onset score.
- Use generator seed 27014. Keep held-out labels in evaluator-only storage. Inference receives no root labels or fault schedule.
- The generator intentionally gives each modality partial, noisy root information. This tests score combination under known artificial conditions only.

## Arms and fixed analysis

- A: neural-like score only.
- B: symbolic-like score only.
- C: equal-weight neural-like plus normalized topology score.
- D: equal-weight neural-like, topology, and temporal scores.
- E: equal-weight neural-like, topology, temporal, and symbolic-like scores.
- Normalize each modality by within-case average rank mapped to [0,1]; use arithmetic mean across included modalities. Ties use stable service-ID order.
- Report Top-1, Top-3, MRR, false diagnosis among non-abstained cases, abstention rate (top-two margin < 0.05), coverage, and explanation coverage. The synthetic path explanation is the supplied graph path from predicted root to the highest-scored reachable service; path correctness is checked against generated affected descendants.
- Report 95% Wilson intervals for Top-1 and paired bootstrap intervals (10,000 resamples, seed 17015) for E minus strongest independent arm. The campaign's +5 percentage-point target is descriptive here and not a real-data acceptance.

## Execution controls

Identical held-out inputs and generator, CPU, deterministic scripts, no network. The prediction process must not load labels. Seal prediction hash before evaluation. An independent script recomputes reported metrics from predictions and evaluator-only labels.

## Limits

Synthetic modalities encode the generator's assumptions. No feature has a calibrated real-world unit or established operational meaning. The study cannot validate actual system fusion, causality, RCAEval performance, or service-level generalization.
