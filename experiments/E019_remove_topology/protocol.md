# E019-R001 protocol — frozen before implementation

Date: 2026-11-07 (Asia/Calcutta). Stage XP016. Generate 600 fresh 10-service cases with seed 29016 using the frozen E017 generator. Keep labels evaluator-only.

- Full arm: equal mean of within-case rank scores for neural, topology, temporal, and symbolic modalities.
- Topology-disabled arm: equal mean of neural, temporal, and symbolic scores. Graph edges/outdegree are not read for its ranking; it emits no graph-path explanation.
- Same inputs, tie policy, score transforms, CPU environment, and abstention threshold (top-two margin <0.05).
- Report Top-1/Top-3/MRR, paired differences with 10,000 bootstrap resamples seed 19016, false diagnosis, abstention, coverage, explanation coverage and path accuracy.
- Seal predictions before opening labels; independently recompute metrics and verify the disabled arm's rank scores depend only on non-topology modalities.

All features are generated and have no real RCA semantics.
