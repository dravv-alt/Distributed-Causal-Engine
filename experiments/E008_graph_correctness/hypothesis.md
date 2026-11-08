# E008 research question and hypothesis

**Question:** Does the existing typed graph builder preserve a controlled set of directed, evidence-backed topology relations and the expected paths, cycles, shared dependencies, scoped identities, and reachable impact sets?

**Hypothesis:** Given valid resources and dependencies, the builder preserves node identity, edge direction, relation type, evidence, and multi-edge structure; invalid endpoint or evidence references are rejected. Reachability will match an independent adjacency-list oracle.

**Independent variables:** graph topology structure (branching, shared downstream node, cycle, isolated node, environment-scoped identities) and invalid relation fixtures.

**Dependent measures:** node/edge/reference fidelity; endpoint/evidence rejection; path and reachability agreement; cycle membership; shared-dependency count; reachable-node coverage.

**Reference:** a fixture declared in configuration and an independent graph oracle implemented without NetworkX or `typed_graph` internals.

**Limits:** All edges are synthetic structural observations with declared evidence references. No edge represents proven causality or an actual dependency in deployed infrastructure. This does not evaluate root-cause accuracy.
