# DCE domain v1 contract

Authoritative executable values: src/dce_foundation/domain.py. This is E003's experimental contract,
not a validated production telemetry schema or a JSON Schema pretending to enforce all dataclass types.

- EventTime: exact epoch_ns, UTC string, source value/field/unit/precision. Receipt time absent for offline data.
- Entity: deterministic environment + opaque source identity. Kind UNKNOWN until justified.
- MetricObservation: named finite numeric value or explicit None, unit nullable, full row provenance.
- LogEvent: message/severity nullable, full source log fields preserved.
- TraceSpan: exact trace/span/parent identities, duration raw; end time/duration unit nullable; status raw.
- Dependency: typed observed relation, source/target identity, evidence IDs and event time; no causal claim.
- FaultEvent/GroundTruth: evaluator-owned source labels/queries; never operational topology truth.
- Incident: explicit half-open replay scope, entities/observations/dependencies, separate ground truth and data-quality ledger.

All source-specific names occur only in the adapter/inspection layer or uninterpreted provenance.
Downstream code must use canonical fields. Unknown semantics retained only in attributes are adequacy gaps,
not approved downstream input contracts. See E003 decision for revisions to identities, units and deployment/resource relations.
