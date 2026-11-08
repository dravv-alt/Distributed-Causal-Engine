"""Run XP005's synthetic graph-fidelity checks against typed_graph."""
from __future__ import annotations

from collections import deque
import hashlib
import json
import platform
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
import networkx as nx
from dce_foundation.representation_v2.model import Dependency, Relation, ResourceKind, SourceRef, resource
from dce_foundation.representation_v2.topology import typed_graph

RUN = EXP / "results" / "E008-R001"
CONFIG = json.loads((EXP / "configuration.json").read_text(encoding="utf-8"))
TOPOLOGY = ROOT / "src" / "dce_foundation" / "representation_v2" / "topology.py"
MODEL = ROOT / "src" / "dce_foundation" / "representation_v2" / "model.py"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_new(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def bfs(start: str, adjacency: dict[str, set[str]]) -> set[str]:
    seen: set[str] = set()
    queue = deque(adjacency.get(start, set()))
    while queue:
        node = queue.popleft()
        if node == start or node in seen:
            continue
        seen.add(node)
        queue.extend(adjacency.get(node, set()) - seen)
    return seen


def main() -> None:
    RUN.mkdir(parents=True, exist_ok=False)
    relevant = [EXP / "README.md", EXP / "hypothesis.md", EXP / "protocol.md",
                EXP / "configuration.json", Path(__file__), MODEL, TOPOLOGY]
    with zipfile.ZipFile(RUN / "source-snapshot.zip", "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in relevant:
            archive.write(path, path.relative_to(ROOT).as_posix())

    source_refs = {key: SourceRef("E008-synthetic", "E008-R001", row,
                                  {"fixture_node": key, "environment": value["environment"]})
                   for row, (key, value) in enumerate(((n["id"], n) for n in CONFIG["nodes"]), start=1)}
    resources = {}
    for node in CONFIG["nodes"]:
        resources[node["id"]] = resource(node["environment"], node["name"],
                                          source_refs[node["id"]], ResourceKind.UNKNOWN)
    reverse_ids = {item.resource_id: key for key, item in resources.items()}
    dependencies = []
    for row, edge in enumerate(CONFIG["edges"], start=1):
        provenance = SourceRef("E008-synthetic", "E008-R001", row,
                               {"fixture_edge": edge["id"]})
        dependencies.append(Dependency(
            dependency_id=edge["id"], source=resources[edge["source"]].resource_id,
            target=resources[edge["target"]].resource_id,
            relation_type=Relation[edge["relation"]], evidence=tuple(edge["evidence"]),
            provenance=provenance))

    graph = typed_graph(list(resources.values()), dependencies)
    expected_nodes = {node["id"] for node in CONFIG["nodes"]}
    actual_nodes = {reverse_ids[node] for node in graph.nodes}
    expected_edges = {(e["id"], e["source"], e["target"], e["relation"], tuple(e["evidence"]))
                      for e in CONFIG["edges"]}
    actual_edges = {
        (key, reverse_ids[source], reverse_ids[target], attrs["relation_type"], tuple(attrs["evidence"]))
        for source, target, key, attrs in graph.edges(keys=True, data=True)
    }

    adjacency: dict[str, set[str]] = {node: set() for node in expected_nodes}
    for edge in CONFIG["edges"]:
        adjacency[edge["source"]].add(edge["target"])
    expected_reachability = {node: bfs(node, adjacency) for node in sorted(expected_nodes)}
    declared_reachability = {node: set(values) for node, values in CONFIG["expected_reachability"].items()}
    actual_reachability = {
        key: {reverse_ids[target] for target in nx.descendants(graph, resources[key].resource_id)}
        for key in sorted(expected_nodes)
    }
    shared = actual_reachability["frontend-a"] & actual_reachability["frontend-b"]

    invalid_endpoint = Dependency(
        "bad-endpoint", "resource:absent", resources["inventory"].resource_id,
        Relation.CALLS, ("fixture:bad:endpoint",), SourceRef("E008-synthetic", "E008-R001", 99, {}))
    invalid_evidence = Dependency(
        "bad-evidence", resources["inventory"].resource_id, resources["database"].resource_id,
        Relation.CALLS, (), SourceRef("E008-synthetic", "E008-R001", 100, {}))
    rejected_invalid_endpoint = rejected_invalid_evidence = False
    for invalid, label in ((invalid_endpoint, "endpoint"), (invalid_evidence, "evidence")):
        try:
            typed_graph(list(resources.values()), dependencies + [invalid])
        except ValueError:
            if label == "endpoint":
                rejected_invalid_endpoint = True
            else:
                rejected_invalid_evidence = True

    frontend_a = resources["frontend-a"].resource_id
    frontend_prod = resources["frontend-prod"].resource_id
    assertions = {
        "all_seven_nodes_preserved": actual_nodes == expected_nodes and graph.number_of_nodes() == 7,
        "all_six_keyed_edges_and_evidence_preserved": actual_edges == expected_edges and graph.number_of_edges() == 6,
        "environment_scoped_same_name_ids_distinct": frontend_a != frontend_prod,
        "edge_direction_and_relation_fidelity": all(
            graph.has_edge(resources[e["source"]].resource_id, resources[e["target"]].resource_id, key=e["id"])
            and graph[resources[e["source"]].resource_id][resources[e["target"]].resource_id][e["id"]]["relation_type"] == e["relation"]
            for e in CONFIG["edges"]),
        "reachability_matches_independent_bfs": actual_reachability == expected_reachability == declared_reachability,
        "database_cache_cycle_is_mutually_reachable": (
            "cache" in actual_reachability["database"] and "database" in actual_reachability["cache"]),
        "both_frontends_share_expected_downstream": shared == {"inventory", "database", "cache"},
        "isolated_and_production_nodes_have_no_impact_paths": (
            actual_reachability["isolated"] == set() and actual_reachability["frontend-prod"] == set()),
        "invalid_endpoint_rejected": rejected_invalid_endpoint,
        "missing_evidence_rejected": rejected_invalid_evidence,
    }

    git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              capture_output=True, text=True).stdout.strip() or "UNKNOWN"
    git_status = subprocess.run(["git", "status", "--short"], cwd=ROOT,
                                capture_output=True, text=True).stdout.splitlines()
    preflight = {
        "experiment_id": "E008", "run_id": "E008-R001", "python": sys.version,
        "platform": platform.platform(), "network_access": "none",
        "openresearch": "orx unavailable; standalone local runner",
        "networkx_version": nx.__version__, "git_head": git_head,
        "git_status_excerpt": git_status[:100],
        "source_hashes": {path.relative_to(ROOT).as_posix(): sha256(path) for path in relevant},
        "configuration_sha256": sha256(EXP / "configuration.json"),
        "protocol_sha256": sha256(EXP / "protocol.md"),
        "source_snapshot_sha256": sha256(RUN / "source-snapshot.zip")}
    write_new(RUN / "preflight.json", preflight)
    result = {
        "experiment_id": "E008", "run_id": "E008-R001",
        "status": "PASS" if all(assertions.values()) else "REVISE",
        "assertions": assertions,
        "node_count": graph.number_of_nodes(), "edge_count": graph.number_of_edges(),
        "expected_edges": sorted([list(e) for e in expected_edges]),
        "actual_edges": sorted([list(e) for e in actual_edges]),
        "expected_reachability": {k: sorted(v) for k, v in expected_reachability.items()},
        "actual_reachability": {k: sorted(v) for k, v in actual_reachability.items()},
        "shared_downstream": sorted(shared),
        "limitations": ["Synthetic structural fixture only; no real deployment topology was read.",
                        "Reachability is not a causal or fault-propagation claim.",
                        "No RCA metric, fault label, or diagnosis was evaluated."]}
    write_new(RUN / "results.json", result)
    manifest = {"preflight_sha256": sha256(RUN / "preflight.json"),
                "results_sha256": sha256(RUN / "results.json"),
                "snapshot_sha256": sha256(RUN / "source-snapshot.zip"),
                "runner_mode": "offline local deterministic synthetic experiment"}
    write_new(RUN / "source-manifest.json", manifest)
    print(json.dumps({"status": result["status"], "assertions": assertions,
                      "node_count": graph.number_of_nodes(), "edge_count": graph.number_of_edges(),
                      "output": str(RUN / "results.json")}, sort_keys=True))
    if not all(assertions.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
