"""Generate label-blind topology-only predictions from staged traces."""
from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
import json
import platform
import subprocess
import sys
import zipfile
from pathlib import Path

import networkx as nx
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "E009_rcaeval_topology_baseline"
RUN = EXP / "results" / "E009-R001"
CONFIG = json.loads((EXP / "configuration.json").read_text(encoding="utf-8"))
TRACE_FIELDS = ["traceID", "spanID", "serviceName", "parentSpanID"]


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


def blank_case(case_id: str) -> dict:
    return {"blind_case_id": case_id, "trace_available": False, "abstained": True,
            "abstain_reason": "no_trace_file", "candidate_count": 0, "graph_node_count": 0,
            "unique_cross_service_edge_count": 0, "parent_resolution_counts": {},
            "edges": [], "methods": {"topology_shared_callers_v1": [], "graph_disabled_uniform_v1": []},
            "explanation_coverage": 0.0}


def predict(case_id: str, trace_path: Path | None) -> tuple[dict, str | None]:
    if trace_path is None or not trace_path.is_file():
        return blank_case(case_id), None
    frame = pl.read_parquet(trace_path, columns=TRACE_FIELDS)
    records = frame.to_dicts()
    candidates = {row["serviceName"] for row in records
                  if isinstance(row.get("serviceName"), str) and row["serviceName"].strip()}
    identity_counts = Counter()
    for row in records:
        trace_id, span_id = row.get("traceID"), row.get("spanID")
        if isinstance(trace_id, str) and trace_id and isinstance(span_id, str) and span_id:
            identity_counts[(trace_id, span_id)] += 1
    service_for = {}
    for row in records:
        trace_id, span_id = row.get("traceID"), row.get("spanID")
        key = (trace_id, span_id)
        if identity_counts.get(key) == 1:
            service = row.get("serviceName")
            if isinstance(service, str) and service.strip():
                service_for[key] = service

    resolution = Counter()
    edge_references: dict[tuple[str, str], list[str]] = defaultdict(list)
    for row in records:
        trace_id, span_id, parent = row.get("traceID"), row.get("spanID"), row.get("parentSpanID")
        if not trace_id or not span_id:
            resolution["missing_span_identity"] += 1
            continue
        if not isinstance(parent, str) or not parent:
            resolution["missing_parent_or_root_unknown"] += 1
            continue
        parent_key = (trace_id, parent)
        nparents = identity_counts.get(parent_key, 0)
        if nparents == 0:
            resolution["unresolved_parent"] += 1
            continue
        if nparents > 1:
            resolution["ambiguous_parent"] += 1
            continue
        if parent == span_id:
            resolution["self_parent"] += 1
            continue
        parent_service = service_for.get(parent_key)
        child_service = service_for.get((trace_id, span_id))
        if not parent_service or not child_service:
            resolution["missing_service"] += 1
            continue
        if parent_service == child_service:
            resolution["same_service_parent"] += 1
            continue
        # This digest is an opaque evidence reference, not a label or feature.
        evidence = hashlib.sha256(f"{trace_id}\0{parent}\0{span_id}".encode()).hexdigest()[:20]
        edge_references[(parent_service, child_service)].append(evidence)
        resolution["resolved_cross_service_parent"] += 1

    graph = nx.DiGraph()
    graph.add_nodes_from(sorted(candidates))
    for source, target in edge_references:
        graph.add_edge(source, target)
    scores = {node: len(nx.ancestors(graph, node) - {node}) for node in graph.nodes}
    ordered = sorted(scores, key=lambda node: (-scores[node], node))
    topology = [{"service": node, "score": scores[node],
                 "reachable_callers": sorted(nx.ancestors(graph, node) - {node}),
                 "score_kind": "distinct reachable caller services; structural rank only"}
                for node in ordered]
    uniform = [{"service": node, "score": 0, "reachable_callers": [],
                "score_kind": "graph-disabled equal score"}
               for node in sorted(candidates)]
    edges = [{"source": source, "target": target,
              "span_reference_count": len(refs), "evidence_ref_hashes": sorted(refs)}
             for (source, target), refs in sorted(edge_references.items())]
    explained = sum(bool(item["reachable_callers"]) for item in topology)
    result = {
        "blind_case_id": case_id, "trace_available": True,
        "abstained": not candidates,
        "abstain_reason": "empty_service_candidate_set" if not candidates else None,
        "trace_row_count": len(records), "candidate_count": len(candidates),
        "graph_node_count": graph.number_of_nodes(), "graph_edge_count": graph.number_of_edges(),
        "unique_cross_service_edge_count": graph.number_of_edges(),
        "parent_resolution_counts": dict(sorted(resolution.items())),
        "duplicate_span_identity_count": sum(1 for count in identity_counts.values() if count > 1),
        "edges": edges,
        "methods": {"topology_shared_callers_v1": topology,
                    "graph_disabled_uniform_v1": uniform},
        "explanation_coverage": explained / len(topology) if topology else 0.0,
        "explanation_coverage_denominator": len(topology),
    }
    return result, digest(trace_path)


def main() -> None:
    RUN.mkdir(parents=True, exist_ok=False)
    scripts = sorted((EXP / "scripts").glob("*.py"))
    source_paths = [EXP / "README.md", EXP / "hypothesis.md", EXP / "protocol.md",
                    EXP / "configuration.json", *scripts]
    with zipfile.ZipFile(RUN / "source-snapshot.zip", "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in source_paths:
            archive.write(path, path.relative_to(ROOT).as_posix())

    all_predictions = []
    input_hashes = {}
    for case_id in CONFIG["blind_case_ids"]:
        path = ROOT / "data" / "rcaeval" / "inference" / case_id / "traces.parquet"
        prediction, file_hash = predict(case_id, path if path.is_file() else None)
        if file_hash:
            input_hashes[path.relative_to(ROOT).as_posix()] = file_hash
        all_predictions.append(prediction)

    pred_path = RUN / "predictions.jsonl"
    with pred_path.open("x", encoding="utf-8", newline="\n") as stream:
        for prediction in all_predictions:
            stream.write(json.dumps(prediction, sort_keys=True) + "\n")
        stream.flush()

    git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip() or "UNKNOWN"
    git_status = subprocess.run(["git", "status", "--short"], cwd=ROOT,
                                capture_output=True, text=True).stdout.splitlines()
    preflight = {"run_id": "E009-R001", "execution_mode": "standalone local; no network",
                 "orx": "unavailable on PATH", "dataset_revision": CONFIG["revision"],
                 "python": sys.version, "platform": platform.platform(),
                 "polars_version": pl.__version__, "networkx_version": nx.__version__,
                 "git_head": git_head, "git_status_excerpt": git_status[:100],
                 "model_input_allowlist": TRACE_FIELDS,
                 "model_input_hashes": input_hashes,
                 "source_hashes": {path.relative_to(ROOT).as_posix(): digest(path) for path in source_paths},
                 "source_snapshot_sha256": digest(RUN / "source-snapshot.zip"),
                 "prediction_sha256": digest(pred_path),
                 "prediction_rows": len(all_predictions)}
    emit(RUN / "preflight.json", preflight)
    seal = {"prediction_file": pred_path.relative_to(ROOT).as_posix(),
            "prediction_sha256": digest(pred_path), "prediction_rows": len(all_predictions),
            "seal_created_before_evaluator_label_access": True,
            "label_inputs_opened_by_prediction_process": False}
    emit(RUN / "prediction-seal.json", seal)
    print(json.dumps({"prediction_rows": len(all_predictions),
                      "trace_cases": sum(p["trace_available"] for p in all_predictions),
                      "prediction_sha256": seal["prediction_sha256"],
                      "output": str(pred_path)}, sort_keys=True))


if __name__ == "__main__":
    main()
