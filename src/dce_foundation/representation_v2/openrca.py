"""Strict v2 source mapping; evaluation labels never enter this adapter."""
from decimal import Decimal, InvalidOperation
from pathlib import PurePosixPath
from dataclasses import replace
from ..domain import digest
from ..telemetry.openrca import HEADERS
from .model import SourceRef, Observation, ResourceKind, resource, MetricRegistry
from .timestamps import classify


def map_record(scenario, path, line, row, interpretation, start, end, registry=None):
    name = PurePosixPath(path).name
    expected = HEADERS.get(scenario.split('/')[0], {}).get(name)
    if expected is None or set(row) != set(expected):
        return "unsupported", [], None, "unsupported header"
    if None in row or any(v is None for v in row.values()):
        return "rejected", [], None, "field count mismatch"
    field = "startTime" if "startTime" in row else "timestamp"
    state, ns = classify(row[field], interpretation, start, end)
    if state != "mapped":
        return "rejected" if state == "invalid" else state, [], None, "timestamp:" + state
    raw_name = row.get("cmdb_id") or row.get("service") or row.get("tc") or row.get("serviceName")
    source_key = digest(["OpenRCA", scenario, path])
    prov = SourceRef("OpenRCA", source_key, line, dict(row),
                     {"timestamp_unit": interpretation["selected_unit"], "timestamp_field": field,
                      "profile_status": interpretation["status"]})
    # Metric filenames name collection scopes, not guaranteed deployment resource kinds.
    kind = ResourceKind.SERVICE if name in ("metric_service.csv",) and "service" in row else ResourceKind.UNKNOWN
    try:
        res = resource(scenario, raw_name, prov, kind)
        oid = "observation:" + digest([source_key, line])
        quality = tuple("missing:" + k for k,v in row.items() if v == "")
        common = dict(object_id=oid, event_ns=ns, resource_id=res.resource_id, provenance=prov, quality=quality)
        if name.startswith("log_"):
            return "mapped", [Observation(signal="log", message=row["value"] or None, **common)], res, None
        if name == "trace_span.csv":
            trace = row.get("trace_id", row.get("traceId"))
            span = row.get("span_id", row.get("id"))
            if not trace or not span:
                raise ValueError("missing trace/span identity")
            duration = row.get("duration", row.get("elapsedTime")) or None
            if duration is not None:
                d = Decimal(duration)
                if not d.is_finite() or d < 0:
                    raise ValueError("invalid duration")
            return "mapped", [Observation(signal="span", trace_id=trace, span_id=span,
                parent_span_id=row.get("parent_id", row.get("parent_span", row.get("pid"))) or None,
                service=row.get("serviceName") or None, duration_raw=duration,
                status_raw=row.get("status_code", row.get("success")) or None, **common)], res, None
        values = [(row.get("kpi_name", row.get("name")), row["value"])] if "value" in row else [
            (k,v) for k,v in row.items() if k not in {field,"tc","service","serviceName"}]
        observations = []
        registry = registry or MetricRegistry()
        for metric, value in values:
            if not metric:
                raise ValueError("missing metric name")
            if value and not Decimal(value).is_finite():
                raise ValueError("nonfinite metric")
            args = dict(common)
            args["object_id"] += ":" + digest(metric)
            observations.append(Observation(signal="metric", metric=registry.lookup(scenario + ":" + name, metric),
                                            value=value or None, **args))
        return "mapped", observations, res, None
    except (ValueError, InvalidOperation) as exc:
        return "rejected", [], None, str(exc)


def inference_view(observation, window):
    """Allowlisted projection: no paths, raw attributes, labels or source row order."""
    if not window.start_ns <= observation.event_ns <= window.query_ns or observation.signal not in window.modalities:
        return None
    result = {"object_id": observation.object_id, "signal": observation.signal,
              "event_ns": observation.event_ns, "resource_id": observation.resource_id}
    if observation.signal == "metric":
        result.update(metric_name=observation.metric.metric_name, value=observation.value,
                      unit=observation.metric.unit, temporality=observation.metric.temporality, kind=observation.metric.kind)
    elif observation.signal == "span":
        result.update(trace_id=observation.trace_id, span_id=observation.span_id,
                      parent_span_id=observation.parent_span_id, duration_raw=observation.duration_raw,
                      duration_unit=observation.duration_unit, status_raw=observation.status_raw)
    else:
        # Free text is quarantined until a content leakage policy is reviewed.
        result.update(severity=observation.severity, message_available=observation.message is not None)
    return result
