# E033-R001 provenance review — 2026-11-08

This additive review preserves the protocol, original run artifacts, decision, and permanent register.

## Integrity and data separation

- Recomputed all 22 artifact-manifest entries; every listed file exists and matches its recorded byte count and SHA-256 hash.
- Recomputed the `diagnoses.json` and `inputs.json` hashes; both match `prediction-seal.json`, which records that evaluator root labels were not loaded.
- The stored evaluation's outcome and root-label hashes match `sandbox-outcomes.json` and the evaluator-only label fixture. The independent audit reports PASS and recomputes root/path selection from the encoded graph.

## Result and construction limits

The stored evaluation reports 300/300 cases with the database selected as root and the full declared path recovered. The propagation method always uses one `repair_database` action and the simulator defines that action as clearing all symptoms. The baseline always uses three symptom actions, and the simulator defines those symptoms as recurring while the database root fault remains active.

Inspection of the generator confirms all 300 cases use the same four-node directed chain, all four symptoms active, and the same database ground-truth root; only onset jitter varies. The transition simulator assigns recovery directly from whether the action list contains `repair_database`. Thus the perfect result is guaranteed by the encoded graph and action-effect rules. The audit independently recomputes those rules but shares the same synthetic mechanism assumptions; it is not an independent recovery oracle.

This is a narrow mechanism-wiring sanity check. It does not establish general cascade localization, real recovery, service behavior, or self-healing effectiveness.

## Provenance and governance discrepancy

The listed artifact hashes are consistent, but a frozen Git revision/clean source snapshot at run time is not recorded; that provenance remains unknown.

The E033 amendment maps XP030 to E033. The permanent experiment index and XP030 stage card remain unchanged; the stage is still recorded as planned/not authorized and the permanent identity unallocated. This review preserves that conflict and does not authorize advancement.

## Bounded disposition

The run demonstrates that the implementation follows a deliberately fixed synthetic chain and its prewritten effect model. The stored suggestion to continue to XP031 is not a reviewed gate decision; claims about real cascades remain UNKNOWN.
