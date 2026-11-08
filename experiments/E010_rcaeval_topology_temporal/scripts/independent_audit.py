"""Recompute E010 temporal features/ranks without importing its predictor."""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "E010_rcaeval_topology_temporal"
RUN = EXP / "results" / "E010-R001"
CFG = json.loads((EXP / "configuration.json").read_text(encoding="utf-8"))
E009 = ROOT / "experiments" / "E009_rcaeval_topology_baseline" / "results" / "E009-R001"
FIELDS = ["traceID", "spanID", "serviceName", "parentSpanID", "startTimeMillis"]


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def emit(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def scale(values: dict[str, int]) -> dict[str, float]:
    if not values or max(values.values()) == min(values.values()):
        return {k: 0.0 for k in values}
    low, high = min(values.values()), max(values.values())
    return {k: (v - low) / (high - low) for k, v in values.items()}


def rank(values: dict[str, float | int]) -> list[dict]:
    return [{"service": k, "score": values[k]} for k in sorted(values, key=lambda k: (-values[k], k))]


def independent_temporal(rows: list[dict], services: set[str]) -> tuple[dict, dict[str, list[dict]]]:
    if not rows:
        empty = {"trace_row_count": 0, "candidate_count": 0, "timestamp_range_raw": None,
                 "timestamp_missing_count": 0, "parent_resolution_counts": {},
                 "service_onset_order_raw": [], "temporal_consistency": {},
                 "edge_support": {}, "scores": {}, "order_invariant": True}
        return empty, {}
    stamps = [int(r["startTimeMillis"]) for r in rows if r.get("startTimeMillis") is not None]
    span_range = max(stamps) - min(stamps)
    ids = Counter((r.get("traceID"), r.get("spanID")) for r in rows if r.get("traceID") and r.get("spanID"))
    unique = {(r.get("traceID"), r.get("spanID")): r for r in rows
              if r.get("traceID") and r.get("spanID") and ids[(r.get("traceID"), r.get("spanID"))] == 1}
    edge_deltas: dict[tuple[str, str], list[int]] = defaultdict(list)
    states = Counter()
    first_seen = {}
    for record in rows:
        service, raw_time = record.get("serviceName"), record.get("startTimeMillis")
        if isinstance(service, str) and service.strip() and raw_time is not None:
            first_seen[service] = min(first_seen.get(service, int(raw_time)), int(raw_time))
        parent, trace, span = record.get("parentSpanID"), record.get("traceID"), record.get("spanID")
        if not trace or not span:
            states["missing_span_identity"] += 1
            continue
        if not isinstance(parent, str) or not parent:
            states["missing_parent_or_root_unknown"] += 1
            continue
        parent_count = ids.get((trace, parent), 0)
        if parent_count == 0:
            states["unresolved_parent"] += 1
            continue
        if parent_count > 1:
            states["ambiguous_parent"] += 1
            continue
        if parent == span:
            states["self_parent"] += 1
            continue
        parent_record = unique[(trace, parent)]
        pservice, cservice = parent_record.get("serviceName"), service
        ptime, ctime = parent_record.get("startTimeMillis"), raw_time
        if not isinstance(pservice, str) or not pservice.strip() or not isinstance(cservice, str) or not cservice.strip():
            states["missing_service"] += 1
            continue
        if pservice == cservice:
            states["same_service_parent"] += 1
            continue
        if ptime is None or ctime is None:
            states["missing_pair_timestamp"] += 1
            continue
        edge_deltas[(pservice, cservice)].append(int(ctime) - int(ptime))
        states["resolved_cross_service_parent"] += 1

    total = sum(map(len, edge_deltas.values()))
    score_sets, edge_reports, consistency = {}, {}, {}
    for fraction in CFG["relative_delay_bounds"]:
        key = f"{fraction:.2f}"
        bound = max(1, math.floor(span_range * fraction))
        scores = Counter()
        edges, supported_total = {}, 0
        for (src, dst), deltas in sorted(edge_deltas.items()):
            passing = [d for d in deltas if 0 <= d <= bound]
            supported = len(passing) / len(deltas) >= CFG["temporal_edge_support_threshold"]
            edges[f"{src}\u2192{dst}"] = {
                "references": len(deltas), "supported_references": len(passing),
                "support_fraction": len(passing) / len(deltas), "temporal_edge_supported": supported,
                "raw_delta_min": min(deltas), "raw_delta_max": max(deltas)}
            scores[src] += int(supported)
            supported_total += len(passing)
        score_sets[key] = {service: scores.get(service, 0) for service in services}
        edge_reports[key] = {"bound_fraction": fraction, "bound_raw_units": bound, "supported_edges": edges}
        consistency[key] = supported_total / total if total else None
    feature_report = {
        "trace_row_count": len(rows), "candidate_count": len(services),
        "timestamp_range_raw": {"min": min(stamps), "max": max(stamps), "range": span_range},
        "timestamp_missing_count": sum(r.get("startTimeMillis") is None for r in rows),
        "duplicate_span_identity_count": sum(count > 1 for count in ids.values()),
        "parent_resolution_counts": dict(sorted(states.items())),
        "service_onset_order_raw": [{"service": s, "first_raw_timestamp": t}
                                     for s, t in sorted(first_seen.items(), key=lambda x: (x[1], x[0]))],
        "temporal_consistency": consistency, "edge_support": edge_reports,
        "scores": score_sets, "order_invariant": None}
    ranked = {}
    for key, temporal in score_sets.items():
        topology = rank(temporal)
        temporal_norm = scale(temporal)
        ranked[f"temporal_only_{key}"] = topology
        # Topology scores are filled by caller from the frozen E009 baseline.
        ranked[f"_temporal_norm_{key}"] = temporal_norm
    return feature_report, ranked


def main() -> None:
    pred_path = RUN / "predictions.jsonl"
    seal = json.loads((RUN / "prediction-seal.json").read_text(encoding="utf-8"))
    if digest(pred_path) != seal["prediction_sha256"]:
        raise ValueError("E010 predictions changed after seal")
    e009_path = E009 / "predictions.jsonl"
    e009_seal = json.loads((E009 / "prediction-seal.json").read_text(encoding="utf-8"))
    if digest(e009_path) != e009_seal["prediction_sha256"]:
        raise ValueError("E009 baseline seal mismatch")
    base = {p["blind_case_id"]: p for p in (json.loads(line) for line in e009_path.read_text(encoding="utf-8").splitlines())}
    actual = [json.loads(line) for line in pred_path.read_text(encoding="utf-8").splitlines()]
    expected_case_ids = set(CFG["blind_case_ids"])
    checks, diff, input_hashes = {}, {}, {}
    frozen_hashes = json.loads((E009 / "preflight.json").read_text(encoding="utf-8"))["model_input_hashes"]
    for pred in actual:
        cid = pred["blind_case_id"]
        path = ROOT / "data" / "rcaeval" / "inference" / cid / "traces.parquet"
        if path.is_file():
            raw_hash = digest(path)
            input_hashes[path.relative_to(ROOT).as_posix()] = raw_hash
            if frozen_hashes.get(path.relative_to(ROOT).as_posix()) != raw_hash:
                raise ValueError(f"trace input differs from E009: {cid}")
            frame = pl.read_parquet(path, columns=FIELDS)
            rows = frame.to_dicts()
            service_set = {r["serviceName"] for r in rows if isinstance(r.get("serviceName"), str) and r["serviceName"].strip()}
            recomputed, partial = independent_temporal(rows, service_set)
            reverse, _ = independent_temporal(list(reversed(rows)), service_set)
            invariance_fields = [k for k in recomputed if k != "order_invariant"]
            row_order_ok = all(recomputed[k] == reverse[k] for k in invariance_fields)
            recomputed["order_invariant"] = row_order_ok
            topo = base[cid]["methods"]["topology_shared_callers_v1"]
            topo_scores = {r["service"]: r["score"] for r in topo}
            topo_norm = scale(topo_scores)
            expected_methods = {"topology_only_e009": topo,
                                "graph_disabled_uniform_e009": base[cid]["methods"]["graph_disabled_uniform_v1"]}
            for b in [f"{x:.2f}" for x in CFG["relative_delay_bounds"]]:
                expected_methods[f"temporal_only_{b}"] = rank(recomputed["scores"][b])
                tn = scale(recomputed["scores"][b])
                combo = {s: topo_norm[s] + tn[s] for s in service_set}
                expected_methods[f"topology_temporal_{b}"] = rank(combo)
            baseline_ok = pred["topology_only"] == topo and pred["uniform"] == base[cid]["methods"]["graph_disabled_uniform_v1"]
            feature_ok = pred["temporal"] == recomputed
            methods_ok = pred["methods"] == expected_methods
            same = row_order_ok and baseline_ok and feature_ok and methods_ok and pred["candidate_count"] == len(service_set)
            if not same:
                diff[cid] = {"row_order_ok": row_order_ok, "baseline_ok": baseline_ok,
                             "feature_match": feature_ok, "method_match": methods_ok}
        else:
            same = pred["candidate_count"] == 0 and pred["trace_available"] is False
            if pred["temporal"].get("trace_row_count") != 0:
                same = False
        checks[cid] = same
    report = {"status": "PASS" if set(checks) == expected_case_ids and all(checks.values()) else "FAIL",
              "audit": "independent label-blind raw timestamp/edge/ranking recomputation",
              "checks": checks, "all_cases_match": bool(checks) and all(checks.values()),
              "prediction_sha256": seal["prediction_sha256"], "e009_baseline_sha256": e009_seal["prediction_sha256"],
              "trace_input_hashes": input_hashes, "differences": diff, "labels_opened": False}
    emit(RUN / "independent-audit.json", report)
    print(json.dumps({"status": report["status"], "cases": len(checks)}, sort_keys=True))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
