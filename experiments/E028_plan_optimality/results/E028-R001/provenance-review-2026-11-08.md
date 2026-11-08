# E028-R001 provenance review — 2026-11-08

This is an additive, read-only review of the existing XP025 synthetic run. It does not edit or replace the frozen protocol, result artifacts, decision, or experiment register.

## Integrity checks performed

- Recomputed every entry in `artifact-manifest.json`: all 19 listed files exist and match their recorded byte counts and SHA-256 hashes.
- Recomputed the sealed hashes for `plans.json` and `fixtures/inputs.json`; both match `prediction-seal.json`.
- The seal records `external_labels_loaded: false`, `actions_executed: false`, and `network_used: false`.
- The stored independent audit reports PASS. Its source independently reconstructs candidate feasibility and utility for the declared two-action synthetic set, then checks selection against the exhaustive maximum. It shares the frozen assumptions, action values, and objective with the experiment; it is not an independent real-world action oracle.

## Result and limits

The stored evaluation reports 400 generated states, 244 with at least one feasible candidate, and 72 with multiple candidates. In all 244 feasible states the selected candidate matched the maximum under the declared utility formula. Mean utility gain over the minimum-cost feasible candidate was 0.003646 under that same formula.

This verifies arithmetic and selection within the frozen, synthetic candidate set. It does not validate the objective weights, recovery/risk values, action feasibility for a real system, operational optimality, or remediation safety. No uncertainty estimate is applicable to this deterministic enumeration as conducted; the 400 generated states are not an independent service population.

## Provenance and governance discrepancy

The run has file-level manifests and hashes, but its stored provenance does not establish a frozen Git commit or clean source tree for the protocol, code, and inputs at execution time. That provenance element remains unknown.

The dated E028 amendment allocates XP025 to E028, while `EXPERIMENT_INDEX.md` still lists E003 as the latest permanent identity and the XP025 stage card says the permanent experiment is unallocated and the stage is planned/not authorized. This review preserves that discrepancy; it does not reconcile the records or treat the run as authorized by the index.

## Bounded disposition

Integrity checks passed for the listed artifacts. Scientific scope remains synthetic objective maximization only, with operational plan optimality UNKNOWN. The stored decision's proposed continuation to XP026 is not authorization under the unchanged roadmap and register. Resolve the record conflict through a separately reviewed additive governance amendment before treating E028 as a canonical permanent-register result or advancing dependent work.
