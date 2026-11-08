"""Generate blind E010 temporal and fused scores from trace-only data."""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import math
import platform
import subprocess
import sys
import zipfile
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "E010_rcaeval_topology_temporal"
RUN = EXP / "results" / "E010-R001"
CFG = json.loads((EXP / "configuration.json").read_text(encoding="utf-8"))
E009_RUN = ROOT / "experiments" / "E009_rcaeval_topology_baseline" / "results" / "E009-R001"
TRACE_FIELDS = ["traceID", "spanID", "serviceName", "parentSpanID", "startTimeMillis"]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def emit(path: Path, payload: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")


def rank(rows: dict[str, float | int]) -> list[dict]:
    return [{"service": name, "score": rows[name]} for name in sorted(rows, key=lambda x: (-rows[x], x))]


def normalize(scores: dict[str, int]) -> dict[str, float]:
    if not scores:
        return {}
    low, high = min(scores.values()), max(scores.values())
    if high == low:
        return {name: 0.0 for name in scores}
    return {name: (value - low) / (high - low) for name, value in scores.items()}


def empty_temporal() -> dict:
    return {"trace_row_count": 0, "candidate_count": 0, "timestamp_range_raw": None,
            "timestamp_missing_count": 0, "parent_resolution_counts": {},
            "service_onset_order_raw": [], "temporal_consistency": {},
            "edge_support": {}, "scores": {}, "order_invariant": True}


def temporal_features(rows: list[dict], candidates: set[str]) -> dict:
    if not rows:
        return empty_temporal()
    times = [int(r["startTimeMillis"]) for r in rows if r.get("startTimeMillis") is not None]
    missing_time = sum(r.get("startTimeMillis") is None for r in rows)
    if not times:
        raise ValueError("trace rows have no usable raw ordering timestamps")
    time_range = max(times) - min(times)
    identity_counts = Counter((r.get("traceID"), r.get("spanID")) for r in rows
                              if r.get("traceID") and r.get("spanID"))
    records_by_id = {(r.get("traceID"), r.get("spanID")): r for r in rows
                     if r.get("traceID") and r.get("spanID")
                     and identity_counts[(r.get("traceID"), r.get("spanID"))] == 1}
    resolution = Counter()
    edge_deltas: dict[tuple[str, str], list[int]] = defaultdict(list)
    onset: dict[str, int] = {}
    for row in rows:
        service = row.get("serviceName")
        stamp = row.get("startTimeMillis")
        if isinstance(service, str) and service.strip() and stamp is not None:
            onset[service] = min(onset.get(service, int(stamp)), int(stamp))
        trace_id, span_id, parent = row.get("traceID"), row.get("spanID"), row.get("parentSpanID")
        if not trace_id or not span_id:
            resolution["missing_span_identity"] += 1
            continue
        if not isinstance(parent, str) or not parent:
            resolution["missing_parent_or_root_unknown"] += 1
            continue
        n = identity_counts.get((trace_id, parent), 0)
        if n == 0:
            resolution["unresolved_parent"] += 1
            continue
        if n > 1:
            resolution["ambiguous_parent"] += 1
            continue
        if parent == span_id:
            resolution["self_parent"] += 1
            continue
        parent_row = records_by_id.get((trace_id, parent))
        parent_service = parent_row.get("serviceName") if parent_row else None
        child_service = service
        parent_time = parent_row.get("startTimeMillis") if parent_row else None
        child_time = stamp
        if not isinstance(parent_service, str) or not parent_service.strip() or not isinstance(child_service, str) or not child_service.strip():
            resolution["missing_service"] += 1
            continue
        if parent_service == child_service:
            resolution["same_service_parent"] += 1
            continue
        if parent_time is None or child_time is None:
            resolution["missing_pair_timestamp"] += 1
            continue
        edge_deltas[(parent_service, child_service)].append(int(child_time) - int(parent_time))
        resolution["resolved_cross_service_parent"] += 1

    scores_by_bound: dict[str, dict[str, int]] = {}
    edge_support: dict[str, dict] = {}
    consistency: dict[str, float | None] = {}
    total_refs = sum(len(deltas) for deltas in edge_deltas.values())
    for fraction in CFG["relative_delay_bounds"]:
        key = f"{fraction:.2f}"
        bound = max(1, math.floor(time_range * fraction))
        supported_edges = {}
        per_source = Counter()
        supported_refs = 0
        for (source, target), deltas in sorted(edge_deltas.items()):
            good = sum(0 <= delta <= bound for delta in deltas)
            fraction_good = good / len(deltas)
            supported = fraction_good >= CFG["temporal_edge_support_threshold"]
            supported_edges[f"{source}\u2192{target}"] = {
                "references": len(deltas), "supported_references": good,
                "support_fraction": fraction_good, "temporal_edge_supported": supported,
                "raw_delta_min": min(deltas), "raw_delta_max": max(deltas)}
            if supported:
                per_source[source] += 1
            supported_refs += good
        scores_by_bound[key] = {name: per_source.get(name, 0) for name in candidates}
        edge_support[key] = {"bound_fraction": fraction, "bound_raw_units": bound,
                             "supported_edges": supported_edges}
        consistency[key] = supported_refs / total_refs if total_refs else None

    onset_order = [{"service": service, "first_raw_timestamp": stamp}
                   for service, stamp in sorted(onset.items(), key=lambda x: (x[1], x[0]))]
    return {"trace_row_count": len(rows), "candidate_count": len(candidates),
            "timestamp_range_raw": {"min": min(times), "max": max(times), "range": time_range},
            "timestamp_missing_count": missing_time,
            "duplicate_span_identity_count": sum(n > 1 for n in identity_counts.values()),
            "parent_resolution_counts": dict(sorted(resolution.items())),
            "service_onset_order_raw": onset_order,
            "temporal_consistency": consistency, "edge_support": edge_support,
            "scores": scores_by_bound,
            "order_invariant": None}


def build_case(case_id: str, trace_path: Path | None, e009: dict) -> tuple[dict, str | None]:
    topology = e009["methods"]["topology_shared_callers_v1"]
    uniform = e009["methods"]["graph_disabled_uniform_v1"]
    topo_names = {row["service"] for row in topology}
    uniform_names = {row["service"] for row in uniform}
    if topo_names != uniform_names or len(topo_names) != e009["candidate_count"]:
        raise ValueError(f"E009 method candidate sets disagree for {case_id}")
    if trace_path is None or not trace_path.is_file():
        if topo_names:
            raise ValueError(f"E009 has candidates but E010 trace is absent for {case_id}")
        empty_methods = {"topology_only_e009": topology,
                         "graph_disabled_uniform_e009": uniform}
        for fraction in CFG["relative_delay_bounds"]:
            bound = f"{fraction:.2f}"
            empty_methods[f"temporal_only_{bound}"] = []
            empty_methods[f"topology_temporal_{bound}"] = []
        return {"blind_case_id": case_id, "trace_available": False, "abstained": True,
                "candidate_count": 0, "topology_only": topology, "uniform": uniform,
                "temporal": empty_temporal(), "methods": empty_methods,
                "row_order_exact": True}, None
    rows = pl.read_parquet(trace_path, columns=TRACE_FIELDS).to_dicts()
    candidates = {r["serviceName"] for r in rows if isinstance(r.get("serviceName"), str) and r["serviceName"].strip()}
    if candidates != topo_names:
        raise ValueError(f"trace/E009 candidate mismatch for {case_id}")
    features = temporal_features(rows, candidates)
    reversed_features = temporal_features(list(reversed(rows)), candidates)
    for key in ("trace_row_count", "candidate_count", "timestamp_range_raw", "timestamp_missing_count",
                "duplicate_span_identity_count", "parent_resolution_counts", "service_onset_order_raw",
                "temporal_consistency", "edge_support", "scores"):
        if features[key] != reversed_features[key]:
            raise ValueError(f"row-order invariance failed for {case_id}: {key}")
    features["order_invariant"] = True
    methods = {"topology_only_e009": topology, "graph_disabled_uniform_e009": uniform}
    topo_scores = {row["service"]: row["score"] for row in topology}
    norm_topo = normalize(topo_scores)
    for bound, temporal_scores in features["scores"].items():
        methods[f"temporal_only_{bound}"] = rank(temporal_scores)
        norm_temp = normalize(temporal_scores)
        combined = {service: norm_topo[service] + norm_temp[service] for service in candidates}
        methods[f"topology_temporal_{bound}"] = rank(combined)
    output = {"blind_case_id": case_id, "trace_available": True, "abstained": not candidates,
              "candidate_count": len(candidates), "topology_only": topology, "uniform": uniform,
              "temporal": features, "methods": methods,
              "row_order_exact": features["order_invariant"]}
    return output, digest(trace_path)


def main() -> None:
    e009_seal_path = E009_RUN / "prediction-seal.json"
    e009_predictions_path = E009_RUN / "predictions.jsonl"
    e009_preflight = json.loads((E009_RUN / "preflight.json").read_text(encoding="utf-8"))
    e009_seal = json.loads(e009_seal_path.read_text(encoding="utf-8"))
    if digest(e009_predictions_path) != e009_seal["prediction_sha256"]:
        raise ValueError("E009 predictions no longer match their seal")
    frozen_input_hashes = e009_preflight["model_input_hashes"]
    for rel, expected in frozen_input_hashes.items():
        if digest(ROOT / rel) != expected:
            raise ValueError(f"E009 trace input changed: {rel}")
    e009_rows = {row["blind_case_id"]: row for row in
                 (json.loads(line) for line in e009_predictions_path.read_text(encoding="utf-8").splitlines())}
    if set(e009_rows) != set(CFG["blind_case_ids"]):
        raise ValueError("E009 baseline population does not match E010 frozen population")

    RUN.mkdir(parents=True, exist_ok=False)
    sources = [EXP / "README.md", EXP / "hypothesis.md", EXP / "protocol.md",
               EXP / "configuration.json", *sorted((EXP / "scripts").glob("*.py"))]
    with zipfile.ZipFile(RUN / "source-snapshot.zip", "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for source in sources:
            archive.write(source, source.relative_to(ROOT).as_posix())

    predictions, trace_hashes = [], {}
    for case_id in CFG["blind_case_ids"]:
        path = ROOT / "data" / "rcaeval" / "inference" / case_id / "traces.parquet"
        row, file_hash = build_case(case_id, path if path.is_file() else None, e009_rows[case_id])
        predictions.append(row)
        if file_hash:
            trace_hashes[path.relative_to(ROOT).as_posix()] = file_hash
    pred_path = RUN / "predictions.jsonl"
    with pred_path.open("x", encoding="utf-8", newline="\n") as stream:
        for row in predictions:
            stream.write(json.dumps(row, sort_keys=True) + "\n")
        stream.flush()
    git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip() or "UNKNOWN"
    git_status = subprocess.run(["git", "status", "--short"], cwd=ROOT,
                                capture_output=True, text=True).stdout.splitlines()
    emit(RUN / "preflight.json", {
        "run_id": "E010-R001", "mode": "standalone local; no network; OpenResearch unavailable",
        "dataset_revision": CFG["revision"], "python": sys.version, "platform": platform.platform(),
        "polars_version": pl.__version__, "git_head": git_head, "git_status_excerpt": git_status[:100],
        "trace_input_hashes": trace_hashes, "e009_baseline_prediction_sha256": e009_seal["prediction_sha256"],
        "e009_input_hashes": frozen_input_hashes,
        "source_hashes": {path.relative_to(ROOT).as_posix(): digest(path) for path in sources},
        "source_snapshot_sha256": digest(RUN / "source-snapshot.zip"),
        "prediction_sha256": digest(pred_path), "prediction_rows": len(predictions),
        "evaluator_inputs_opened": False})
    emit(RUN / "prediction-seal.json", {
        "prediction_sha256": digest(pred_path), "prediction_rows": len(predictions),
        "e009_baseline_sha256": e009_seal["prediction_sha256"],
        "sealed_before_evaluator_access": True, "evaluator_inputs_opened": False})
    print(json.dumps({"run_id": "E010-R001", "prediction_rows": len(predictions),
                      "trace_cases": len(trace_hashes), "prediction_sha256": digest(pred_path),
                      "output": str(pred_path)}, sort_keys=True))


if __name__ == "__main__":
    main()
