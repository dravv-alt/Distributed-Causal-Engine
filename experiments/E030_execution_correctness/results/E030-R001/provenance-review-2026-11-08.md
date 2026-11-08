# E030-R001 provenance review — 2026-11-08

This additive review preserves the original protocol, run, result, decision, and experiment register.

## Integrity checks performed

- Recomputed every entry in `artifact-manifest.json`: all 19 listed files exist and match the recorded byte counts and SHA-256 hashes.
- Recomputed the hashes for `transitions.json` and `fixtures/inputs.json`; both match `prediction-seal.json`.
- The seal records `external_actions: false` and `network_used: false`.
- The stored independent audit reports PASS. Its separate oracle implementation recomputes the four transitions and checks the healthy-replica invariant and rollback snapshot equality.

## Result and limits

The stored evaluation reports exact predicted/observed state agreement for 200/200 in-memory cases: 50 each for restart, scale, reroute, and rollback. Rollback restored the supplied snapshot in 50/50 cases.

This establishes agreement between two implementations of a small state simulator for the declared operations. The simulator does not invoke a DCE executor, container, service, filesystem action, or distributed system. Runtime action behavior and operational safety remain UNKNOWN.

## Provenance and governance discrepancy

The listed artifacts are internally hash-consistent, but the run does not establish a frozen Git revision or clean source snapshot at execution; that provenance remains unknown.

The dated E030 amendment maps XP027 to E030. The permanent experiment index and XP027 stage card remain unchanged; the card says the permanent identity is unallocated, the stage is planned/not authorized, and the E003 review barrier remains. This review preserves that mismatch and does not change the canonical register.

## Bounded disposition

The simulator's declared transition contract passed. The stored suggestion to continue to XP028 is not a reviewed gate decision, and this result cannot be presented as actual DCE executor correctness.
