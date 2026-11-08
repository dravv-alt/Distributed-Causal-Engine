# E030-R001 protocol — frozen before implementation

Date 2026-11-07 (Asia/Calcutta). Stage XP027. Generate 200 cases (50 each for restart, scale, reroute, rollback), seed 30027. Before simulated execution, compute predicted state. Execute only against a fresh in-memory Python dictionary. Independently compute oracle state in a separate evaluator script.

- Restart increments restart generation while preserving healthy replica count.
- Scale adds one replica and one healthy replica.
- Reroute changes the route to the requested target.
- Rollback restores the supplied pre-change state exactly.
- Report exact transition agreement, per-action agreement, rollback equality, exceptions and state safety invariants. No process, service, file, or remote system is modified.

The absence of a runnable DCE testbed means these are simulator results only.
