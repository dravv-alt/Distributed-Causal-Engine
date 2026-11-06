# DCE v2 canonical semantics

Implementation: `src/dce_foundation/representation_v2/model.py`. Independent of HTTP, UI, brokers, notebooks and benchmark schemas.

| Value | Meaning | Known / unknown policy |
|---|---|---|
| SourceRef | source name, opaque source key, logical record/cell row, exact attributes and interpretation evidence | Source paths live in the provenance catalog; inference projection omits them. |
| Resource | exact source identity scoped to environment; explicit kind, canonical/source name, namespace, aliases and provenance | UNKNOWN is valid. No name-pattern typing or alias merge. Reviewed aliases are supported by values; no unreviewed aliases applied by adapter. |
| Observation (metric) | event time, resource, original numeric string, named semantics entry | Numeric validity checked with Decimal. No rounding or guessed unit. Wide rows expand to individual metrics with shared row provenance. |
| Observation (log) | event time, resource, source text, UNKNOWN severity | Exact message remains in protected provenance/storage. Free text is omitted from current inference projection pending leakage policy. |
| Observation (span) | trace/span/parent IDs, start time, resource, optional source service, raw duration/status | Missing service/parent explicit. Duration unit, end time and status meaning remain UNKNOWN. No guessed end time or root marker. |
| MetricSemantics | source and canonical names, unit, kind, aggregation, temporality, description and source evidence | Registry accepts documented declarations only. Unknown entry by default. |
| Dependency | typed directed endpoints, record/cell evidence, source reference, event time when available | CALLS, RUNS_ON, DEPENDS_ON, READS_FROM, WRITES_TO, HOSTS. Adapter currently emits only CALLS/RUNS_ON. All OBSERVED; none causal. Workbook validity is UNKNOWN. |
| FaultEvent | evaluator's point annotation, target, reason/type, provenance | No end time. No inferred fault interval. |
| Incident | evaluator association and optional query window | Query-to-fault association UNKNOWN; row counts/order do not define it. |
| GroundTruth | evaluator root identity, injection time, fault type and optional indicator | Separate evaluator storage. OpenRCA structured root indicator UNKNOWN. |
| QueryWindow | start, query cutoff, allowed signals and no-future policy | Observation projection excludes event times outside the declared closed window. Full query-time graph filtering is not yet qualified. |

Trace groups are persisted as environment/trace/span-indexed rows. Context retrieval is bounded by the selected records. Parent state is one of missing_parent_or_root_unknown, self_parent_convention_unknown, unresolved_parent, ambiguous_parent, resolved_parent. A unique resolved parent produces parent resource → child resource CALLS evidence. Missing context is never completed from timestamp similarity.

The domain separates observations and external truth. No reasoning candidate, causal hypothesis or diagnosis object is created during remediation.
