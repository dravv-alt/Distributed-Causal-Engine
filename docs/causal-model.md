# Causal model and claim boundary

Current inference proposes root hypotheses from learned anomalies, dependency structure and temporal evidence.
It does not identify causal effects solely by naming a graph causal. A dependency graph is not automatically a structural causal model.

For causal-estimation experiments, declare variables, interventions, outcome horizon, assumed graph, confounders,
identifiability assumptions and negative controls. Distinguish injected root labels, observed impact and inferred origins.
Shared workload/infrastructure can cause correlated symptoms; cause-before-effect alone is insufficient.

Simulator experiments validate behavior under simulator assumptions. Real testbed interventions and held-out environments
are required for stronger external claims. Keep fault schedules/ground truth out of inference inputs.
Counterfactual claims require a separately specified and validated model; they are not current R0 capabilities.
