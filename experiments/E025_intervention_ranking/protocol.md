# E025-R001 protocol — frozen before implementation

Date 2026-11-07 (Asia/Calcutta). Stage XP022. Generate 600 cases balanced across CPU saturation, database saturation, and network-path bottlenecks; seed 25022. Inputs expose noisy normalized indicators, but not mechanism labels or intervention outcomes.

- Candidate actions: `scale_service`, `repair_database`, `reroute_traffic`.
- Frozen predicted recovery score: `clip(0.10 + 0.75*matching_indicator + 0.05*each_other_indicator, 0, 1)`.
- Each case has evaluator-only controlled recovery outcomes for all three actions. Matching action has mean recovery 0.85, nonmatching actions mean 0.15, plus fixed noise.
- Report best-action accuracy, pairwise ranking consistency, mean absolute recovery error across actions, and per-action ranking/outcome results.
- Inference is label/outcome-blind; seal predictions before evaluation. Independent audit recomputes predictions and metrics.

This is a designed simulation; indicator meaning, treatment effectiveness, and noise are not empirically estimated. No real action, service, or causal claim is involved.
