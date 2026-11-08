# E010-R001 decision proposal

**Technical integrity:** unchanged E009 inputs/baseline were verified; nine blind predictions were sealed before evaluator access; independent raw-trace recomputation matched temporal and fused outputs; reversed row order produced identical results; independent evaluator recomputation matched metrics.

**Observed method result:** topology-plus-temporal produced 11.1% tie-aware Top-1 and 11.1% Top-3, versus E009 topology-only at 0.0% and 7.4%. The temporal consistency feature saturated at 100% for all 170,239 eligible cross-service references at every tested bound. All results are on nine selected cases; five abstained due to absent traces.

**Proposed outcome:** **REVISE / insufficient evidence for XP007 qualification.** The apparent Top-1 change is descriptive and unheld-out; the temporal feature is saturated, timestamp semantics are unknown, and Top-3 trails the matched uniform reference. Do not claim qualified temporal reasoning, fault propagation, or improved RCA from this run.

**Human review:** pending. This proposal does not block the user's request to continue to XP008, but it does not automatically approve or establish that stage.
