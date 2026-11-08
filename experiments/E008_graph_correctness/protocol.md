# E008 protocol v1 — typed graph correctness

## Frozen fixture

Construct two environment-scoped `frontend` resources (`staging`, `production`) with distinct IDs; `frontend-a`, `frontend-b`, `inventory`, `database`, `cache`, and `isolated` within a synthetic staging environment. Add the following directed, evidence-backed edges:

1. `frontend-a -> inventory` (`CALLS`)
2. `frontend-b -> inventory` (`CALLS`)
3. `inventory -> database` (`CALLS`)
4. `database -> cache` (`DEPENDS_ON`)
5. `cache -> database` (`DEPENDS_ON`), creating a directed cycle
6. A second parallel `frontend-a -> inventory` relation with a distinct dependency ID and evidence reference

The reference graph is declared in the frozen config. The isolated resource has no edges. This graph provides two source nodes sharing downstream nodes, a cycle, a parallel relation, an isolated node, and same-named resources with separate environment scopes.

## Measures and oracle

Use `typed_graph` only to build the graph. Independently check resource IDs against the fixture, and edge tuples against the config. Compute expected reachability with a local adjacency-list breadth-first search that does not import NetworkX. Check all source-to-target paths, cycle reachability in both directions between database/cache, shared downstream nodes from both frontends, and the exact reachable set from each frontend and the isolated node. Verify every relation type, edge key, and evidence reference remains present. Verify invalid endpoint and missing-evidence fixtures raise `ValueError`.

## Acceptance

All seven nodes and six keyed edges are represented exactly; environment-scoped IDs stay distinct; the graph builder preserves declared directions, relation types and evidence; each invalid fixture is rejected; BFS reachability agrees with the independent expected sets; database/cache are mutually reachable; both staging frontends reach the shared inventory/database/cache subgraph; and isolated plus the production frontend reach no other node. Any failed invariant is reported; no automatic repair or causal reinterpretation is allowed.

These are engineering invariants for this fixture, not population estimates or scientific accuracy thresholds.

## Execution boundary and provenance

Use local deterministic synthetic records only, no labels, external data, or network. Record Python/platform, package versions, code/config/protocol hashes, Git HEAD/dirty status, exact command, source snapshot and outputs. `orx` is unavailable locally, so execution is standalone and must not be described as OpenResearch-managed.
