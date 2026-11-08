# E034-R001 provenance review — 2026-11-08

This additive review preserves the original experiment files and the permanent register.

## Integrity and data separation

- Recomputed all 23 artifact-manifest entries; every listed file exists and matches its recorded size and SHA-256 hash.
- Recomputed the input and diagnosis hashes; both match `prediction-seal.json`, which records that neither the root schedule nor evaluator labels were loaded during diagnosis.
- The stored evaluation's outcomes and root-label hashes match the corresponding local files. The independent audit reports PASS and recomputes root sets, action results, and action-order comparisons.

## Result and construction limits

The stored evaluation reports exact root-set recovery and in-memory recovery in 300/300 generated cases. The single-root baseline recovered 200/300 overall and 0/100 joint cases; reversing the two multi-root actions changed no final state.

The generator samples clearly separated synthetic indicators (Normal(0.9, 0.1) for present roots and Normal(0.1, 0.1) for absent roots), then applies a fixed 0.6 threshold. The sandbox clears only the matching Boolean fault key; database and network actions therefore commute by construction. A single-root plan necessarily leaves one root active in joint cases. These are controlled toy mechanics, not realistic fault interactions or service recovery. The audit independently recomputes the rules but shares the same simulator assumptions.

## Provenance and governance discrepancy

The listed artifact hashes are consistent, but no frozen Git revision/clean source snapshot at execution is recorded; that provenance remains unknown.

The E034 amendment maps XP031 to E034, while the permanent index and XP031 stage card remain unchanged. This review preserves that discrepancy and does not authorize XP032.

## Bounded disposition

The run is a synthetic multi-root/action-order sanity check only. It does not establish effective diagnosis or safe combined remediation in a real system; the stored suggestion to continue is not a reviewed gate decision.
