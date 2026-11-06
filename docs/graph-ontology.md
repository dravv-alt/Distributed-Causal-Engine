# Graph ontology

Edge depends_on(A, B) means A calls or requires B. Investigate symptoms at A by traversing outgoing dependencies.
Potential impact of B follows reverse dependencies. Observed impact requires telemetry evidence and is distinct from reachability.

Node types: service, datastore, cache, gateway and shared infrastructure. Node identity includes environment and service/instance scope.
Edges record source (operator, traces, configuration), validity interval, observation confidence and topology version.
Missing traces do not prove no edge. Cycles are permitted and traversal must terminate with bounded search.

Validate unknown references, duplicate IDs, edge direction, cycles and version boundaries. The delivered R0 graph
uses service nodes and has simpler metadata; richer ontology is planned, not already implemented.
