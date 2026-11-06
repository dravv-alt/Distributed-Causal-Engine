"""Read-only ZIP adapter; schema profiles follow inspected source headers."""
from collections import Counter, defaultdict
import csv
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
import io
import math
from pathlib import Path, PurePosixPath
import zipfile

from ..domain import (Dependency, Entity, FaultEvent, GroundTruth, Incident,
                      LogEvent, MetricObservation, Provenance, TraceSpan, digest)
from ..event_time import normalize_time

SCENARIOS = ("Bank", "Market/cloudbed-1", "Market/cloudbed-2", "Telecom")
LONG = ("timestamp", "cmdb_id", "kpi_name", "value")
TELECOM_LONG = ("itemid", "name", "bomc_id", "timestamp", "value", "cmdb_id")
LOG = ("log_id", "timestamp", "cmdb_id", "log_name", "value")
HEADERS = {
    "Bank": {
        "trace_span.csv": ("timestamp", "cmdb_id", "parent_id", "span_id", "trace_id", "duration"),
        "metric_app.csv": ("timestamp", "rr", "sr", "cnt", "mrt", "tc"),
        "metric_container.csv": LONG, "log_service.csv": LOG,
    },
    "Market": {
        "trace_span.csv": ("timestamp", "cmdb_id", "span_id", "trace_id", "duration", "type", "status_code", "operation_name", "parent_span"),
        "metric_service.csv": ("service", "timestamp", "rr", "sr", "mrt", "count"),
        **{f"metric_{k}.csv": LONG for k in ("container", "node", "runtime", "mesh")},
        "log_service.csv": LOG, "log_proxy.csv": LOG,
    },
    "Telecom": {
        "trace_span.csv": ("callType", "startTime", "elapsedTime", "success", "traceId", "id", "pid", "cmdb_id", "dsName", "serviceName"),
        "metric_app.csv": ("serviceName", "startTime", "avg_time", "num", "succee_num", "succee_rate"),
        **{f"metric_{k}.csv": TELECOM_LONG for k in ("middleware", "service", "container", "node")},
    },
}
LABEL_HEADERS = {
    "query.csv": {"task_index", "instruction", "scoring_points"},
    "record.csv": {"level", "component", "timestamp", "datetime", "reason"},
}


class SchemaError(ValueError):
    pass


def entity_id(scenario: str, raw: str) -> str:
    if not raw or raw.strip() != raw:
        raise ValueError("missing identity or surrounding whitespace: not silently normalized")
    # JSON tuple encoding avoids collisions from separators; keep original ID unchanged.
    return "entity:" + digest([scenario, raw])


class OpenRCAAdapter:
    def __init__(self, root: str | Path):
        self.root = Path(root)

    def archive(self, scenario: str) -> Path:
        if scenario not in SCENARIOS:
            raise ValueError(f"unsupported scenario {scenario}")
        return self.root / (scenario.split("/")[0] + ".zip")

    def rows(self, scenario: str, path: str):
        with zipfile.ZipFile(self.archive(scenario)) as archive:
            with archive.open(path) as stream:
                reader = csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8-sig", newline=""))
                if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
                    raise SchemaError(f"empty/duplicate headers: {path}")
                for line, row in enumerate(reader, 2):
                    yield line, row, tuple(reader.fieldnames)

    def labels(self, scenario: str, name="record.csv"):
        result = []
        for line, row, headers in self.rows(scenario, f"{scenario}/{name}"):
            if set(headers) != LABEL_HEADERS[name] or None in row or any(v is None for v in row.values()):
                raise SchemaError(f"invalid label schema/row {scenario}/{name}:{line}")
            result.append((line, row))
        return result

    def incident_ids(self, scenario: str) -> list[str]:
        return [f"{scenario}@{line}" for line, _ in self.labels(scenario)]

    def first_incident(self, scenario: str) -> str:
        line, _ = min(self.labels(scenario), key=lambda pair: (normalize_time(pair[1]["timestamp"], "timestamp", "s").epoch_ns, pair[0]))
        return f"{scenario}@{line}"

    def load(self, incident_id: str, max_rows_per_file: int | None = None) -> Incident:
        scenario, sep, row_id = incident_id.rpartition("@")
        if not sep or not row_id.isdigit():
            raise ValueError("incident ID must be <scenario>@<record.csv line>, e.g. Bank@2")
        if max_rows_per_file is not None and max_rows_per_file < 1:
            raise ValueError("row cap must be positive")
        records = self.labels(scenario)
        selected = next((r for line, r in records if line == int(row_id)), None)
        if selected is None:
            raise ValueError("incident source row does not exist")
        time = normalize_time(selected["timestamp"], "timestamp", "s")
        # Directory dates are source-local UTC+8, not UTC day dates.
        dt = datetime.fromtimestamp(time.epoch_ns // 10**9, timezone(timedelta(hours=8)))
        midnight = dt.replace(hour=0, minute=0, second=0, microsecond=0)
        start = int(midnight.timestamp()) * 10**9
        end = start + 86400 * 10**9
        date = dt.strftime("%Y_%m_%d")
        incident = Incident(incident_id, scenario, start, end)
        incident.metadata = {"schema_version": "dce-domain-v1", "adapter_version": "openrca-v1",
            "window": "UTC+08:00 source-local day [start,end); not incident duration",
            "files": {}, "issues": [], "unknown_fields": [], "unmapped_semantics": [],
            "max_rows_per_file": max_rows_per_file, "date": date}
        prefix = f"{scenario}/telemetry/{date}/"
        with zipfile.ZipFile(self.archive(scenario)) as archive:
            paths = sorted(i.filename for i in archive.infolist() if i.filename.startswith(prefix) and i.filename.endswith(".csv"))
        if not paths:
            raise SchemaError(f"no telemetry for selected day: {prefix}")
        system = scenario.split("/")[0]
        for path in paths:
            name = PurePosixPath(path).name
            if name not in HEADERS[system]:
                raise SchemaError(f"unsupported telemetry file: {path}")
            stats = {"scanned": 0, "mapped_rows": 0, "rejected": 0, "outside_window": 0,
                     "duplicates": 0, "out_of_order": 0, "truncated": False, "missing_fields": {},
                     "entities": [], "sampling_delta_ns": {}, "header": list(HEADERS[system][name])}
            incident.metadata["files"][path] = stats
            seen = set()
            previous = None
            entity_names = set()
            per_entity_time = {}
            cadences = Counter()
            missing = Counter()
            for line, row, headers in self.rows(scenario, path):
                # Audit header even in bounded mode; unknown fields cannot silently pass.
                if set(headers) != set(HEADERS[system][name]):
                    raise SchemaError(f"unsupported header {path}: {headers}")
                if max_rows_per_file is not None and stats["scanned"] >= max_rows_per_file:
                    stats["truncated"] = True
                    break
                stats["scanned"] += 1
                try:
                    if None in row or any(v is None for v in row.values()):
                        raise SchemaError("CSV field count mismatch")
                    for key, value in row.items():
                        if value == "":
                            missing[key] += 1
                    duplicate = digest(row) in seen
                    seen.add(digest(row))
                    observations = self.map_row(scenario, path, line, row)
                    event_ns = observations[0].time.epoch_ns
                    if previous is not None and event_ns < previous:
                        stats["out_of_order"] += 1
                    previous = event_ns
                    if not start <= event_ns < end:
                        stats["outside_window"] += 1
                        continue
                    stats["duplicates"] += int(duplicate)
                    if duplicate:
                        observations = [replace(o, provenance=replace(o.provenance, quality=o.provenance.quality + ("duplicate_preserved",))) for o in observations]
                    for o in observations:
                        raw_id = row.get("cmdb_id") or row.get("service") or row.get("tc") or row.get("serviceName")
                        incident.entities[o.entity_id] = Entity(o.entity_id, raw_id, scenario)
                        entity_names.add(raw_id)
                        sampling_key = (o.entity_id, o.name) if isinstance(o, MetricObservation) else None
                        if sampling_key is not None:
                            prev = per_entity_time.get(sampling_key)
                            if prev is not None and event_ns > prev:
                                cadences[event_ns-prev] += 1
                            per_entity_time[sampling_key] = event_ns
                    incident.observations.extend(observations)
                    stats["mapped_rows"] += 1
                except (ValueError, InvalidOperation) as exc:
                    stats["rejected"] += 1
                    incident.metadata["issues"].append({"path": path, "row": line, "error": str(exc), "source_fields": row})
            stats["entities"] = sorted(entity_names)
            stats["missing_fields"] = dict(sorted(missing.items()))
            stats["sampling_delta_ns"] = {str(k): v for k,v in sorted(cadences.items())}
        incident.observations.sort(key=lambda o: (o.time.epoch_ns, o.provenance.path, o.provenance.row, o.id))
        incident.dependencies, parent_issues = self.dependencies(incident)
        incident.metadata["parent_resolution"] = parent_issues
        faults = []
        for line, row in records:
            t = normalize_time(row["timestamp"], "timestamp", "s")
            if start <= t.epoch_ns < end:
                eid = entity_id(scenario, row["component"])
                faults.append(FaultEvent("fault:" + digest([scenario,line]), t, eid, row["reason"] or None,
                    Provenance("OpenRCA", f"{scenario}/record.csv", line, dict(row))))
        faults.sort(key=lambda f: (f.time.epoch_ns, f.id))
        # Queries remain exclusively in ground truth, never operational metadata/graph.
        queries = tuple({**row, "source_row": str(line)} for line,row in self.labels(scenario, "query.csv"))
        incident.ground_truth = GroundTruth(incident_id, tuple(faults), queries)
        return incident

    def map_row(self, scenario, path, line, row):
        system = scenario.split("/")[0]
        name = PurePosixPath(path).name
        if name not in HEADERS[system] or set(row) != set(HEADERS[system][name]):
            raise SchemaError(f"unsupported fields in {path}")
        raw_id = row.get("cmdb_id") or row.get("service") or row.get("tc") or row.get("serviceName")
        eid = entity_id(scenario, raw_id)
        field = "startTime" if "startTime" in row else "timestamp"
        unit = "ms" if system == "Telecom" or name == "trace_span.csv" else "s"
        time = normalize_time(row[field], field, unit)
        quality = tuple("missing:" + k for k,v in row.items() if v == "")
        prov = Provenance("OpenRCA", path, line, dict(row), quality)
        oid = "observation:" + digest([scenario,path,line])
        if name.startswith("log_"):
            return [LogEvent(oid,time,eid,row["value"] or None,None,prov)]
        if name == "trace_span.csv":
            trace = row.get("trace_id", row.get("traceId"))
            span = row.get("span_id", row.get("id"))
            if not trace or not span:
                raise ValueError("missing trace/span identity")
            parent = row.get("parent_id", row.get("parent_span", row.get("pid"))) or None
            duration = row.get("duration", row.get("elapsedTime")) or None
            if duration is not None:
                d = Decimal(duration)
                if not d.is_finite() or d < 0:
                    raise ValueError("invalid span duration")
            return [TraceSpan(oid,time,eid,trace,span,parent,duration,None,None,
                row.get("status_code", row.get("success")) or None,prov)]
        if "value" in row:
            values = [(row.get("kpi_name",row.get("name")),row["value"])]
        else:
            identity = {field, "tc", "service", "serviceName"}
            values = [(k,v) for k,v in row.items() if k not in identity]
        result = []
        for metric,value in values:
            if not metric:
                raise ValueError("missing metric name")
            number = None if value == "" else float(value)
            if number is not None and not math.isfinite(number):
                raise ValueError("nonfinite metric value")
            result.append(MetricObservation(oid+":"+metric,time,eid,metric,number,None,prov))
        return result

    @staticmethod
    def dependencies(incident):
        spans = [o for o in incident.observations if isinstance(o,TraceSpan)]
        index = defaultdict(list)
        for span in spans:
            index[(span.trace_id,span.span_id)].append(span)
        deps = []
        issues = {"missing_parent": 0,"ambiguous_parent": 0,"resolved_parent": 0,"root_marker_or_empty": 0,"self_parent": 0}
        for child in spans:
            # Only empty is known absent. Nonempty sentinel conventions remain unknown.
            if child.parent_span_id is None:
                issues["root_marker_or_empty"] += 1
                continue
            parents = index[(child.trace_id,child.parent_span_id)]
            if not parents:
                issues["missing_parent"] += 1
                continue
            if len(parents) != 1:
                issues["ambiguous_parent"] += 1
                continue
            parent = parents[0]
            if parent.id == child.id:
                issues["self_parent"] += 1
                continue
            issues["resolved_parent"] += 1
            deps.append(Dependency("dependency:"+digest([parent.id,child.id]),parent.entity_id,child.entity_id,
                "CALLS",(parent.id,child.id),child.time))
        return sorted(deps,key=lambda d:d.id),issues
