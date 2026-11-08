# E028-R001 protocol — frozen before implementation

Date 2026-11-07 (Asia/Calcutta). Stage XP025. Generate 400 synthetic maintenance states with seed 28025, minimum healthy replicas 2 and budgets 1/2/4/7. Candidate plans must complete the maintenance restart goal and respect availability/budget constraints.

Feasible plans and fixed attributes:

- `restart_one`: available if initial replicas >=3 and budget >=2; expected recovery .65, cost 2, risk .25, disruption 1, reversibility .80.
- `scale_one_then_restart`: available if replicas >=2 and budget >=7; expected recovery .85, cost 7, risk .12, disruption 1, reversibility .90.

Objective to maximize: `.45*expected_recovery - .15*(cost/7) - .15*risk - .15*(disruption/1) + .10*reversibility`. Enumerate all feasible candidates and compare planner choice to the exhaustive maximum. Report objective components, regret, feasibility, and cases with multiple alternatives. No unlisted action or criterion may be called optimal.

No action execution; all values are synthetic preferences, not approved operating policy.
