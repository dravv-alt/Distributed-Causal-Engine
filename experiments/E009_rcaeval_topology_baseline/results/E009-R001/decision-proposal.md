# E009-R001 decision proposal

**Technical integrity:** predictions were sealed before evaluator-label access; all nine blind predictions matched an independent graph-and-score recomputation; the independent evaluator audit reproduced the reported metrics.

**Observed method result:** topology shared-callers scored below the graph-disabled uniform reference on tie-aware Top-1 (0.0% vs 4.3%) and Top-3 (7.4% vs 12.9%) in this selected nine-case sample. Root candidate coverage was 4/9 for both methods; both abstained on the five cases without traces.

**Proposed outcome:** **REVISE / topology-only heuristic not supported as a useful standalone ranker by this bounded sample.** The result does not establish that topology is generally useless; the sample is small and selected, trace coverage is partial, and root-name matching is exact. No post-hoc tuning was performed.

**Human review:** pending. This proposal is not an approved decision. It does not promote E004's earlier result or establish XP006 completion over the full RCAEval population. The next campaign stage remains XP007 (topology plus temporal evidence) under the user's instruction to continue sequentially.
