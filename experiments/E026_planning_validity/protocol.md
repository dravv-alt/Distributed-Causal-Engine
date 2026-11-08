# E026-R001 protocol — frozen before implementation

Date 2026-11-07 (Asia/Calcutta). Stage XP023. Generate 400 synthetic states with seed 26023, fixed diagnosis/state facts and goal latency <=100 ms.

Action contract:

- `repair_database`: precondition `database_saturated`; clears it and reduces latency by 120 ms.
- `scale_service`: precondition `service_overloaded`; clears it and reduces latency by 100 ms.
- `reroute_traffic`: precondition `network_congested`; clears it and reduces latency by 80 ms.
- Latency is floored at zero; each action can be used once.

The planner repeatedly selects the applicable unused action with largest declared reduction while the goal is unmet. If no action applies, it returns no plan. The independent verifier separately checks each precondition/effect and final goal. Report applicable-plan rate, transition correctness, feasible-goal attainment, infeasible false-plan rate and failures. All states and action effects are synthetic; no execution is authorized.
