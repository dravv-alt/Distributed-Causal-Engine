"""Read-only independent audit of the preserved E008-R001 graph fixture output."""
from __future__ import annotations

from collections import deque
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/E008_graph_correctness"
RUN = EXP / "results/E008-R001"
OUT = RUN / "independent-audit-addendum-2026-11-08.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reachable(start: str, adjacency: dict[str, set[str]]) -> set[str]:
    seen: set[str] = set()
    queue = deque(adjacency[start])
    while queue:
        node = queue.popleft()
        if node == start or node in seen:
            continue
        seen.add(node)
        queue.extend(adjacency[node] - seen)
    return seen


def main() -> None:
    config_path = EXP / "configuration.json"
    preflight_path = RUN / "preflight.json"
    result_path = RUN / "results.json"
    snapshot_path = RUN / "source-snapshot.zip"
    manifest_path = RUN / "source-manifest.json"
    config = json.loads(config_path.read_text(encoding="utf-8"))
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    result = json.loads(result_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    expected_edges = sorted([
        [edge["id"], edge["source"], edge["target"], edge["relation"], edge["evidence"]]
        for edge in config["edges"]
    ])
    actual_edges = sorted(result["actual_edges"])
    expected_nodes = {node["id"] for node in config["nodes"]}
    adjacency = {node: set() for node in expected_nodes}
    for edge in config["edges"]:
        adjacency[edge["source"]].add(edge["target"])
    expected_bfs = {node: reachable(node, adjacency) for node in sorted(expected_nodes)}
    saved_bfs = {node: set(values) for node, values in result["actual_reachability"].items()}
    config_reachability = {node: set(values) for node, values in config["expected_reachability"].items()}

    checks = {
        "preflight_hash_matches_manifest": sha256(preflight_path) == manifest["preflight_sha256"],
        "result_hash_matches_manifest": sha256(result_path) == manifest["results_sha256"],
        "snapshot_hash_matches_both_records": (
            sha256(snapshot_path) == manifest["snapshot_sha256"] == preflight["source_snapshot_sha256"]
        ),
        "all_frozen_source_hashes_match": all(
            (ROOT / relative).is_file() and sha256(ROOT / relative) == expected
            for relative, expected in preflight["source_hashes"].items()
        ),
        "node_count_matches_fixture": len(expected_nodes) == result["node_count"] == 7,
        "edge_inventory_matches_fixture": expected_edges == actual_edges and result["edge_count"] == 6,
        "saved_reachability_matches_independent_bfs": saved_bfs == expected_bfs,
        "saved_reachability_matches_config": saved_bfs == config_reachability,
        "all_original_assertions_true": all(result["assertions"].values()),
        "synthetic_scope_and_limits_recorded": len(result["limitations"]) >= 3,
    }
    payload = {
        "audit": "E008-R001 saved-output, fixture, and independent BFS consistency",
        "audit_date": "2026-11-08",
        "scope": "Read-only verification of saved files; no graph experiment rerun",
        "source_files": {
            path.relative_to(ROOT).as_posix(): sha256(path)
            for path in (config_path, preflight_path, result_path, snapshot_path, manifest_path)
        },
        "verifier": Path(__file__).relative_to(ROOT).as_posix(),
        "verifier_sha256": sha256(Path(__file__)),
        "checks": checks,
        "passed": sum(value is True for value in checks.values()),
        "total": len(checks),
        "interpretation_limit": (
            "This audits the saved seven-node synthetic fixture result only. It does not establish "
            "real topology completeness, causal propagation, or root-cause localization."
        ),
    }
    with OUT.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"passed": payload["passed"], "total": payload["total"], "output": str(OUT)}))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
