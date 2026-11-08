# E020-R001 protocol — frozen before implementation

Date: 2026-11-07 (Asia/Calcutta). Stage XP017. Generate 600 fresh 10-service cases with seed 30017 using the frozen E017 generator; keep labels evaluator-only.

- Full: average rank scores for neural, topology, temporal, symbolic.
- Temporal-disabled: average ranks for neural, topology, symbolic only; onset values are not read for its rank or explanation decisions.
- Same cases, transforms, tie policy, threshold (<0.05 top-two margin), and CPU environment.
- Report Top-1/Top-3/MRR, paired differences (10,000 bootstrap resamples, seed 20017), false diagnosis, abstention, coverage, explanation/path accuracy, and whether earliest synthetic onset equals the root label (evaluator-only onset consistency).
- Seal prediction hash before labels are loaded. Independently recompute metrics and reconstruct temporal-disabled scores without onset.

All timestamp values are arbitrary generated values without physical units. This experiment cannot establish temporal correctness on real telemetry.
