# E008-R001 result interpretation

## Observed result

All ten preregistered graph invariants passed on the synthetic fixture. The builder retained seven distinct resources and six keyed edges, including the parallel `frontend-a -> inventory` relations with separate IDs/evidence. Same-named staging and production resources remained distinct. Declared directions, relation types, and evidence references were preserved. An independent adjacency-list BFS matched graph reachability for every node; the database/cache cycle was mutually reachable; both staging frontends reached the expected shared downstream set; and the isolated and production resources had no outgoing impact paths. Invalid endpoint and missing-evidence fixtures raised `ValueError`.

The saved edge inventory, all reachability sets, and assertions are in `results.json`. The source snapshot and environment/hash evidence are in `source-snapshot.zip`, `preflight.json`, and `source-manifest.json`. A separate artifact audit verified the result status, assertions, edge/node counts, and snapshot hash.

## Interpretation boundary

This validates a graph builder on a seven-node fixture, not real deployment completeness or accuracy. Structural reachability is not causal propagation, fault impact, or root-cause localization. The run used no RCAEval labels, no real telemetry, and no production environment. It does not show that real source identifiers or topology relations can be reconstructed correctly.

## Status

E008-R001: **synthetic graph correctness checks passed; XP005 real-topology qualification and independent human review remain pending**. OpenResearch was unavailable, so execution was standalone and local. No prior record was modified.
