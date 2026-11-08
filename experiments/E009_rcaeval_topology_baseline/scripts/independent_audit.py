"""Independently recompute blind graph edges and scores without labels/NetworkX."""
from __future__ import annotations

from collections import Counter, defaultdict, deque
import hashlib
import json
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "E009_rcaeval_topology_baseline"
RUN = EXP / "results" / "E009-R001"
CONFIG = json.loads((EXP / "configuration.json").read_text(encoding="utf-8"))
FIELDS = ["traceID", "spanID", "serviceName", "parentSpanID"]


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


def reachable_callers(node: str, reverse: dict[str, set[str]]) -> set[str]:
    found: set[str] = set()
    pending = deque(reverse.get(node, set()))
    while pending:
        current = pending.popleft()
        if current == node or current in found:
            continue
        found.add(current)
        pending.extend(reverse.get(current, set()) - found)
    return found


def recompute(path: Path | None) -> dict:
    if path is None or not path.is_file():
        return {"candidate_count": 0, "edge_count": 0, "parent_resolution_counts": {},
                "edges": [], "topology": [], "uniform": [], "explanation_coverage": 0.0}
    records = pl.read_parquet(path, columns=FIELDS).to_dicts()
    candidates = {r["serviceName"] for r in records
                  if isinstance(r.get("serviceName"), str) and r["serviceName"].strip()}
    identity_counts = Counter((r.get("traceID"), r.get("spanID")) for r in records
                              if r.get("traceID") and r.get("spanID"))
    by_identity = {(r.get("traceID"), r.get("spanID")): r.get("serviceName") for r in records
                   if r.get("traceID") and r.get("spanID")
                   and identity_counts[(r.get("traceID"), r.get("spanID"))] == 1
                   and isinstance(r.get("serviceName"), str) and r.get("serviceName").strip()}
    edge_refs: dict[tuple[str, str], list[str]] = defaultdict(list)
    states = Counter()
    for r in records:
        trace, span, parent = r.get("traceID"), r.get("spanID"), r.get("parentSpanID")
        if not trace or not span:
            states["missing_span_identity"] += 1
            continue
        if not isinstance(parent, str) or not parent:
            states["missing_parent_or_root_unknown"] += 1
            continue
        n = identity_counts.get((trace, parent), 0)
        if n == 0:
            states["unresolved_parent"] += 1
            continue
        if n > 1:
            states["ambiguous_parent"] += 1
            continue
        if parent == span:
            states["self_parent"] += 1
            continue
        parent_service = by_identity.get((trace, parent))
        child_service = by_identity.get((trace, span))
        if not parent_service or not child_service:
            states["missing_service"] += 1
            continue
        if parent_service == child_service:
            states["same_service_parent"] += 1
            continue
        ref = hashlib.sha256(f"{trace}\0{parent}\0{span}".encode()).hexdigest()[:20]
        edge_refs[(parent_service, child_service)].append(ref)
        states["resolved_cross_service_parent"] += 1
    reverse: dict[str, set[str]] = {service: set() for service in candidates}
    for source, target in edge_refs:
        reverse[target].add(source)
    topology = []
    for node in sorted(candidates, key=lambda x: (-len(reachable_callers(x, reverse)), x)):
        callers = sorted(reachable_callers(node, reverse))
        topology.append({"service": node, "score": len(callers), "reachable_callers": callers,
                         "score_kind": "distinct reachable caller services; structural rank only"})
    uniform = [{"service": node, "score": 0, "reachable_callers": [],
                "score_kind": "graph-disabled equal score"} for node in sorted(candidates)]
    edges = [{"source": source, "target": target, "span_reference_count": len(refs),
              "evidence_ref_hashes": sorted(refs)} for (source, target), refs in sorted(edge_refs.items())]
    explained = sum(bool(row["reachable_callers"]) for row in topology)
    return {"candidate_count": len(candidates), "edge_count": len(edge_refs),
            "parent_resolution_counts": dict(sorted(states.items())), "edges": edges,
            "topology": topology, "uniform": uniform,
            "explanation_coverage": explained / len(topology) if topology else 0.0}


def main() -> None:
    seal = json.loads((RUN / "prediction-seal.json").read_text(encoding="utf-8"))
    pred_path = RUN / "predictions.jsonl"
    if digest(pred_path) != seal["prediction_sha256"]:
        raise ValueError("prediction hash does not match pre-evaluator seal")
    predictions = [json.loads(line) for line in pred_path.read_text(encoding="utf-8").splitlines()]
    checks = {}
    diffs = {}
    input_hashes = {}
    for prediction in predictions:
        case_id = prediction["blind_case_id"]
        trace = ROOT / "data" / "rcaeval" / "inference" / case_id / "traces.parquet"
        recomputed = recompute(trace if trace.is_file() else None)
        actual_hash = digest(trace) if trace.is_file() else None
        recorded_hash = json.loads((RUN / "preflight.json").read_text(encoding="utf-8"))["model_input_hashes"].get(trace.relative_to(ROOT).as_posix())
        same = (
            recomputed["candidate_count"] == prediction["candidate_count"]
            and recomputed["edge_count"] == prediction.get("graph_edge_count", 0)
            and recomputed["edges"] == prediction["edges"]
            and recomputed["parent_resolution_counts"] == prediction["parent_resolution_counts"]
            and recomputed["topology"] == prediction["methods"]["topology_shared_callers_v1"]
            and recomputed["uniform"] == prediction["methods"]["graph_disabled_uniform_v1"]
            and recomputed["explanation_coverage"] == prediction["explanation_coverage"]
            and actual_hash == recorded_hash
        )
        checks[case_id] = same
        if not same:
            diffs[case_id] = {"recomputed": recomputed, "prediction": prediction,
                              "current_input_hash": actual_hash, "sealed_input_hash": recorded_hash}
        if actual_hash:
            input_hashes[case_id] = actual_hash
    report = {"audit": "independent label-blind adjacency-list recomputation",
              "prediction_sha256": seal["prediction_sha256"], "checks": checks,
              "all_cases_match": bool(checks) and all(checks.values()),
              "input_hashes": input_hashes, "differences": diffs,
              "labels_opened": False}
    emit(RUN / "independent-audit.json", report)
    print(json.dumps({"all_cases_match": report["all_cases_match"], "cases": len(checks)}, sort_keys=True))
    if not report["all_cases_match"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
