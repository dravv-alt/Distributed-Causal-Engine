# E032-R001 protocol — frozen before implementation

Date 2026-11-07 (Asia/Calcutta). Stage XP029. Generate 300 cases balanced among CPU, database, and network faults; seed 32029. Create one active fault per case, noisy severity indicators, and a simulated approval flag (80% true, 20% false). True fault labels remain evaluator-only.

- Diagnosis is the maximum observed signal. Map CPU→scale, DB→repair, network→reroute.
- Apply the action in an in-memory simulator only when approval is true. Correct action clears the active fault; wrong action leaves it active and increments a false-remediation counter.
- Logical detection cost is 2 ticks; planning 1 tick; action/verification 3 ticks. Report simulated MTTD/MTTR separately from wall-clock runtime.
- Report diagnosis accuracy, plan validity, recovery, false remediation, and refusal when approval is absent. The approval flag is generated for simulation and is not human review.
- No real services, telemetry, external effects, or production actions.
