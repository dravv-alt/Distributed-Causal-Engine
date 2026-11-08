# E031-R001 provenance review — 2026-11-08

This additive review preserves the existing protocol, run artifacts, decision, and register.

## Integrity and leakage checks

- Recomputed all 27 `artifact-manifest.json` entries; all files exist and match their recorded sizes and SHA-256 hashes.
- Recomputed hashes for the predictions, observed environment outcomes, controller decisions, input cases, failure schedule, and evaluator-only failure labels; they match the stored seals/evaluation references.
- The prediction and controller seals state that the inference/controller did not load the environment schedule or evaluator labels. The environment seal assigns the schedule to the sandbox executor and records that the controller did not open it.
- The stored independent audit reports PASS. Its separate audit code rebuilds detection, dispositions, and snapshot restoration from the inputs, outcomes, and isolated schedule/label fixtures.
- The controller's `rollback_state` is an in-memory representation copied from the initial snapshot. No external rollback took place.

## Result and limits

The stored evaluation reports 240 synthetic scenarios: 120 injected failures detected, zero false alarms among 120 successes, 120 re-diagnosis requests, and 120/120 exact snapshot-state matches in the simulated controller output.

This supports the controller/executor logic for the declared fixture transitions. It does not show that a DCE application detects or recovers from a failed live action, executes rollback, or is safe for self-healing.

## Provenance and governance discrepancy

The file hashes and data separation checks pass. A frozen Git revision/clean source snapshot at execution is not recorded, so that provenance remains unknown.

The E031 dated amendment maps XP028 to E031. The permanent index and XP028 stage card remain unchanged; the stage card still records the identity as unallocated and the stage as planned/not authorized. This note preserves the mismatch and does not authorize the next stage.

## Bounded disposition

The synthetic failure-injection and rollback-state simulation is internally consistent under its declared assumptions. Actual application recovery and safety remain UNKNOWN; the stored suggestion to proceed to XP029 is not a reviewed gate decision.
