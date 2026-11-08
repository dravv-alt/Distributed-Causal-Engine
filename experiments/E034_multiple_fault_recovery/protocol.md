# E034-R001 protocol — frozen before implementation

Date 2026-11-07 (Asia/Calcutta). Stage XP031. Generate 300 cases: 100 DB-only, 100 network-only, 100 DB+network; seed 34031. True root sets remain in the environment/evaluator split.

- Multi-root diagnosis includes each indicator >=0.60; map DB→`repair_database`, network→`reroute_traffic`.
- Baseline diagnoses only the highest signal and selects one action.
- Sandbox actions clear only their corresponding fault. In joint cases, verify final fault set, residual symptoms, and that DB/network action order produces identical final state.
- Report exact root-set accuracy, full recovery rate, single-root baseline recovery, and action-order interference.
- Isolated in-memory simulation only; no live database or network fault is injected.
