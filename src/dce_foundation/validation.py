from collections import Counter
from .domain import MetricObservation, LogEvent, TraceSpan, digest
from .graph import graph_dict


def validate(incident, graph):
    counts=Counter(o.kind for o in incident.observations)
    files=incident.metadata["files"]
    scanned=sum(s["scanned"] for s in files.values())
    mapped=sum(s["mapped_rows"] for s in files.values())
    rejected=sum(s["rejected"] for s in files.values())
    outside=sum(s["outside_window"] for s in files.values())
    roots={f.entity_id for f in incident.ground_truth.events}
    represented=roots & incident.entities.keys()
    metrics=[o for o in incident.observations if isinstance(o,MetricObservation)]
    spans=[o for o in incident.observations if isinstance(o,TraceSpan)]
    violations=[]
    ids=[o.id for o in incident.observations]
    if len(set(ids))!=len(ids): violations.append("duplicate canonical observation IDs")
    if scanned != mapped+rejected+outside: violations.append("record conservation failure")
    if any(o.entity_id not in incident.entities for o in incident.observations): violations.append("unresolved observation entity")
    if any(not incident.start_ns <= o.time.epoch_ns < incident.end_ns for o in incident.observations): violations.append("out-of-window canonical record")
    if any(d.source_entity not in incident.entities or d.target_entity not in incident.entities for d in incident.dependencies): violations.append("unresolved dependency endpoint")
    if any(a.get("category") in ("possible_causal","established_causal") for _,_,a in graph.edges(data=True)): violations.append("causal assertion in observational graph")
    gaps=[]
    if any(s["truncated"] for s in files.values()): gaps.append("bounded prefix scan: full day/event coverage unverified")
    if rejected: gaps.append("source records rejected; inspect issue ledger")
    if roots-represented: gaps.append("label entities absent from sampled telemetry; aliases/coverage unresolved")
    if metrics: gaps.append("metric units/aggregation semantics UNKNOWN; raw values preserved")
    if spans: gaps.append("span duration units/status meanings UNKNOWN; no end time fabricated")
    if incident.metadata["parent_resolution"]["missing_parent"] or incident.metadata["parent_resolution"]["ambiguous_parent"]: gaps.append("trace topology incomplete or ambiguous")
    near={o.entity_id for o in incident.observations for f in incident.ground_truth.events if o.entity_id==f.entity_id and abs(o.time.epoch_ns-f.time.epoch_ns)<=300*10**9}
    # Labels are point events; evidence near labels is a coverage statistic, not causal validation.
    return {"incident":incident.id,"environment":incident.environment,
        "source_rows_scanned":scanned,"source_rows_mapped":mapped,"source_rows_rejected":rejected,
        "source_rows_outside_window":outside,"record_conservation":scanned==mapped+rejected+outside,
        "entities":len(incident.entities),"dependencies":len(incident.dependencies),
        "observations":len(incident.observations),"metrics":counts["metric"],"logs":counts["log"],"spans":counts["span"],
        "events":len(incident.ground_truth.events),"ground_truth_unique_roots":len(roots),
        "ground_truth_roots_observed":len(represented),"roots_with_evidence_within_5min":len(near),
        "unknown_metric_units":sum(o.unit is None for o in metrics),"missing_metric_values":sum(o.value is None for o in metrics),
        "unknown_span_duration_units":sum(o.duration_unit is None for o in spans),
        "duplicates_preserved":sum(s["duplicates"] for s in files.values()),
        "out_of_order_source_records":sum(s["out_of_order"] for s in files.values()),
        "unmappable_fields":incident.metadata["unknown_fields"],"parent_resolution":incident.metadata["parent_resolution"],
        "schema":"PASS" if not violations and not rejected else "FAIL",
        "timestamps":"PASS" if not rejected else "REVIEW_REJECTIONS",
        "topology":"PARTIAL_OBSERVATIONAL" if spans else "NO_TRACE_EVIDENCE",
        "ground_truth":"COVERED_IDENTITIES_ONLY" if roots==represented else "PARTIAL",
        "violations":violations,"adequacy_gaps":gaps,
        "downstream_ready":not gaps and not violations,
        "canonical_digest":digest(incident.to_dict()),"operational_digest":digest(incident.operational_dict()),
        "graph_digest":digest(graph_dict(graph)),"file_statistics":files,"issues":incident.metadata["issues"]}
