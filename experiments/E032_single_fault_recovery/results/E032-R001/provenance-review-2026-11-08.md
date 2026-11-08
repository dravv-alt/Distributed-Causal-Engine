# E032-R001 provenance review — 2026-11-08

This additive review preserves the frozen protocol, original result files, decision, and permanent register.

## Integrity and data separation

- Recomputed all 24 artifact-manifest entries; all files exist and match their recorded sizes and SHA-256 hashes.
- The controller-decision and input hashes match `controller-seal.json`. That seal records that neither the fault schedule nor evaluator labels were loaded by the controller.
- The sandbox-outcome and fault-schedule hashes match `environment-seal.json`; it identifies the sandbox executor as the only consumer of the schedule.
- The evaluator-only label hash matches the stored evaluation provenance. The independent audit reports PASS and its source separately recomputes the fixed signal ranking, action map, simulated approval gate, and outcome counts.

## Result and limits

The stored evaluation reports 300 synthetic single-fault cases. The signal-ranking diagnosis was correct in 170/300 (56.7%). A generated approval flag allowed 248 simulated actions and declined 52; 144 cases recovered, while 104 approved cases applied an action inconsistent with the generated true fault. No simulated action ran without the generated approval flag.

The 2-tick MTTD and 6-tick successful-path MTTR are constants from the protocol, not measured timing. The approval flag is simulated and is not a human approval workflow. All actions and recoveries are in-memory; no service or application was touched. This is not evidence of safe self-healing.

## Provenance and governance discrepancy

Artifact hashes and the stated label/schedule separation are internally consistent. A frozen Git revision/clean source snapshot at run time is not established, so that provenance remains unknown.

The dated E032 amendment maps XP029 to E032, while the permanent index and XP029 stage card remain unchanged. The stage card still says the identity is unallocated and the stage is planned/not authorized. This review preserves the discrepancy and does not approve the next stage.

## Bounded disposition

The simulator measured a weak diagnosis-to-action loop: a simulated approval gate did not prevent wrong actions when diagnosis was wrong. The stored suggestion to continue to XP030 is not a reviewed gate decision. Human-approved service recovery remains untested.
