from __future__ import annotations

import json
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = ROOT / "experiments" / "E016_membership_adaptation" / "fixtures"
CANONICAL = [f"svc-{i:02d}" for i in range(8)]


def make_case(case_id: str, n: int, rng: np.random.Generator) -> tuple[dict, str]:
    nodes = [f"svc-{i:02d}" for i in range(n)]
    root = nodes[int(rng.integers(0, n))]
    edge_probability = min(0.8, 3.0 / max(1, n - 1))
    edges = []
    for i in range(n):
        for j in range(i + 1, n):
            if rng.random() < edge_probability:
                edges.append([nodes[i], nodes[j]])
    children = {name: [] for name in nodes}
    for source, target in edges:
        children[source].append(target)
    descendants = set()
    todo = list(children[root])
    while todo:
        node = todo.pop()
        if node in descendants:
            continue
        descendants.add(node)
        todo.extend(children[node])
    records = []
    for node in nodes:
        values = rng.normal(0.0, 0.75, size=2)
        if node == root:
            values += np.array([2.8, 2.2])
        elif node in descendants:
            values += np.array([1.2, 0.8])
        records.append({"service_id": node, "signals": [float(values[0]), float(values[1])]})
    return {"scenario_id": case_id, "nodes": records, "edges": edges}, root


def main() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    train_inputs, train_labels = [], {}
    train_rng = np.random.default_rng(16013)
    for i in range(300):
        case, root = make_case(f"TRAIN-{i:04d}", 8, train_rng)
        train_inputs.append(case)
        train_labels[case["scenario_id"]] = root
    (FIXTURES / "train-inputs.json").write_text(json.dumps({"version": "synthetic-membership-train-v1", "cases": train_inputs}, indent=2) + "\n", encoding="utf-8")
    (FIXTURES / "train-labels.json").write_text(json.dumps({"case_roots": train_labels}, indent=2) + "\n", encoding="utf-8")

    tests, test_labels = [], {}
    for n, seed in ((8, 18008), (12, 18012), (20, 18020)):
        rng = np.random.default_rng(seed)
        for i in range(100):
            case, root = make_case(f"N{n}-{i:04d}", n, rng)
            tests.append(case)
            test_labels[case["scenario_id"]] = root
    (FIXTURES / "test-inputs.json").write_text(json.dumps({"version": "synthetic-membership-test-v1", "cases": tests}, indent=2) + "\n", encoding="utf-8")
    (FIXTURES / "evaluator-only").mkdir(parents=True, exist_ok=True)
    (FIXTURES / "evaluator-only" / "test-labels.json").write_text(json.dumps({"case_roots": test_labels}, indent=2) + "\n", encoding="utf-8")

    permutation_inputs, permutation_labels = [], {}
    for case in tests[:100]:
        permuted = {"scenario_id": "P-" + case["scenario_id"], "nodes": list(reversed(case["nodes"])), "edges": case["edges"]}
        permutation_inputs.append(permuted)
        permutation_labels[permuted["scenario_id"]] = test_labels[case["scenario_id"]]
    (FIXTURES / "permutation-inputs.json").write_text(json.dumps({"version": "synthetic-membership-permutation-v1", "cases": permutation_inputs}, indent=2) + "\n", encoding="utf-8")
    (FIXTURES / "evaluator-only" / "permutation-labels.json").write_text(json.dumps({"case_roots": permutation_labels}, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"train_cases": len(train_inputs), "test_cases": len(tests), "test_sizes": [8, 12, 20], "permutation_cases": len(permutation_inputs), "labels_separated": True}, indent=2))


if __name__ == "__main__":
    main()
