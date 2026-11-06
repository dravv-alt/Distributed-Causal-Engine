# E004-R001: what we learned

All 335 cases were processed twice. The technical repeatability and independent-audit gate passed.

| Method | Top-1 (tie-aware) | Top-3 (tie-aware) | Abstentions |
|---|---:|---:|---:|
| symbolic_topology_v1 | 3.08% | 8.93% | 0 |
| activity_reference_v1 | 4.78% | 14.93% | 0 |
| graph_disabled_uniform_v1 | 1.80% | 5.41% | 0 |

The labelled component appears among observed candidates in 284/335 cases. Cases without it remain in the denominator.

This ranks structural candidates, not measured faulty symptoms. A heavily shared dependency is not necessarily broken. Missing traces do not prove no dependency. UNKNOWN metric semantics remain unresolved. Supplied fault times define retrospective windows: this is not online detection, official query scoring, causal inference or evidence of hybrid superiority. The descriptive paired intervals do not establish significance under overlapping windows.

Decision proposal: REVISE / restricted diagnostic readiness. Review the results before authorizing symptom qualification or another experiment. No successor has started.

