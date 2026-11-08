# E027-R001 protocol — frozen before implementation

Date 2026-11-07 (Asia/Calcutta). Stage XP024. Generate 400 synthetic maintenance cases with seed 27024. Goal: perform one restart. Hard constraints: minimum healthy replicas 2 at all times; maximum disruption 1; budget 7 cost units.

- `scale_one`: costs 5, adds one healthy replica, zero disruption.
- `restart_one`: costs 2, disruption 1 while in progress, restores its replica on completion. It is allowed only if preconditions hold, disruption is within maximum, and healthy replicas during disruption remain >=2.
- Unconstrained baseline proposes `restart_one` in every case.
- Constrained planner proposes direct restart when healthy replicas >=3; if exactly 2 it proposes scale then restart only when budget permits; otherwise rejects.
- Independent verifier recomputes all intermediate states, cost, disruption, availability, and goal completion. Report baseline violation rate, constrained rejection correctness, false acceptance, and safe-goal coverage.

Offline simulation only. Rejection must happen before action execution. Synthetic constraints do not establish production safety.
