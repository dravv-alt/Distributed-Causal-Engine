from __future__ import annotations

import json
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parents[1]
FIX = BASE / "fixtures"


def make_case(i: int, rng: np.random.Generator) -> tuple[dict, dict]:
    ids = [f"svc-{j:02d}" for j in range(10)]
    root = ids[int(rng.integers(0, len(ids)))]
    remainder = [x for x in ids if x != root]
    rng.shuffle(remainder)
    order = [root] + remainder
    edges = []
    for j in range(1, len(order)):
        parent = order[int(rng.integers(0, j))]
        edges.append([parent, order[j]])
    rank = {node: pos for pos, node in enumerate(order)}
    for a in range(10):
        for b in range(10):
            if rank[ids[a]] < rank[ids[b]] and rng.random() < 0.08:
                edge = [ids[a], ids[b]]
                if edge not in edges:
                    edges.append(edge)
    descendants = set()
    todo = [b for a, b in edges if a == root]
    adjacency = {node: [] for node in ids}
    for a, b in edges:
        adjacency[a].append(b)
    while todo:
        node = todo.pop()
        if node in descendants:
            continue
        descendants.add(node)
        todo.extend(adjacency[node])
    neural = {}
    for node in ids:
        mean = 1.35 if node == root else (0.5 if node in descendants else 0.0)
        neural[node] = float(rng.normal(mean, 1.0))
    symbolic_target = root if rng.random() < 0.62 else ids[int(rng.integers(0, 10))]
    symbolic = {node: (1.0 if node == symbolic_target else 0.0) + float(rng.normal(0, 0.12)) for node in ids}
    onset = {}
    root_time = float(rng.normal(0, 0.25))
    for node in ids:
        if node == root:
            onset[node] = root_time
        elif node in descendants:
            onset[node] = root_time + float(rng.uniform(0.5, 2.0) + rng.normal(0, 0.45))
        else:
            onset[node] = root_time + float(rng.uniform(-0.2, 2.5))
    degree = {node: 0 for node in ids}
    for a, _ in edges:
        degree[a] += 1
    nodes = [{"service_id": node, "neural_signal": neural[node], "symbolic_score": symbolic[node], "onset": onset[node]} for node in ids]
    case = {"scenario_id": f"SYN-{i:04d}", "nodes": nodes, "edges": edges, "out_degree": degree}
    label = {"root": root, "affected_descendants": sorted(descendants)}
    return case, label


def main() -> None:
    FIX.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(27014)
    cases, labels = [], {}
    for i in range(600):
        case, label = make_case(i, rng)
        cases.append(case)
        labels[case["scenario_id"]] = label
    (FIX / "test-inputs.json").write_text(json.dumps({"version": "synthetic-fusion-v1", "cases": cases}, indent=2) + "\n", encoding="utf-8")
    evaluator = FIX / "evaluator-only"
    evaluator.mkdir(parents=True, exist_ok=True)
    (evaluator / "test-labels.json").write_text(json.dumps({"case_labels": labels}, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"heldout_cases": len(cases), "services_per_case": 10, "labels_separated": True, "seed": 27014}, indent=2))


if __name__ == "__main__":
    main()
