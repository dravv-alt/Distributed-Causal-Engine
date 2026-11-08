# E031-R001 protocol — frozen before implementation

Date 2026-11-07 (Asia/Calcutta). Stage XP028. Generate 240 scenarios (40 successes and 40 failures per action: restart, scale, reroute), seed 31028. The failure schedule remains in `fixtures/environment-only/` and is read only by the sandbox executor. The controller receives planned/observed states, never the injection label or schedule.

- Success executor applies the declared action effect. Failure executor applies a partial, absent, or wrong effect by action.
- Controller detects mismatch by exact state comparison. Match→`VERIFIED`; mismatch→`REPLAN_REQUIRED`; mismatch cases roll back to the saved state snapshot.
- Evaluator reports failure detection, false alarms, missed failures, diagnosis re-entry, and exact rollback. Independent audit recomputes all states.
- All transitions occur in memory. No application, service, or external resource is touched.
