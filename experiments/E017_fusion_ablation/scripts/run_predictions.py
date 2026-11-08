from __future__ import annotations

import hashlib
import json
from pathlib import Path
import platform
import sys

import numpy as np

BASE = Path(__file__).resolve().parents[1]
INPUT = BASE / "fixtures" / "test-inputs.json"
RUN = BASE / "results" / "E017-R001"
ARMS = {
    "neural_only": ["neural"],
    "symbolic_only": ["symbolic"],
    "neural_topology": ["neural", "topology"],
    "neural_topology_temporal": ["neural", "topology", "temporal"],
    "full_fusion": ["neural", "topology", "temporal", "symbolic"],
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def ranks(values: dict[str, float]) -> dict[str, float]:
    names = sorted(values)
    ordered = sorted(names, key=lambda name: (-values[name], name))
    # Average rank for exact score ties; map best to 1 and worst to 0.
    result = {}
    i = 0
    while i < len(ordered):
        j = i + 1
        while j < len(ordered) and values[ordered[j]] == values[ordered[i]]:
            j += 1
        avg_rank = (i + 1 + j) / 2
        score = 1.0 - (avg_rank - 1) / max(1, len(ordered) - 1)
        for name in ordered[i:j]:
            result[name] = score
        i = j
    return result


def predict(case: dict) -> dict:
    if set(case) != {"scenario_id", "nodes", "edges", "out_degree"}:
        raise ValueError("unexpected case schema")
    ids = [n["service_id"] for n in case["nodes"]]
    if len(ids) != 10 or len(set(ids)) != len(ids):
        raise ValueError("invalid service membership")
    adjacency = {name: [] for name in ids}
    for edge in case["edges"]:
        if len(edge) != 2 or edge[0] not in adjacency or edge[1] not in adjacency or edge[0] == edge[1]:
            raise ValueError("invalid edge")
        adjacency[edge[0]].append(edge[1])
    by_id = {n["service_id"]: n for n in case["nodes"]}
    raw = {
        "neural": {name: by_id[name]["neural_signal"] for name in ids},
        "symbolic": {name: by_id[name]["symbolic_score"] for name in ids},
        "temporal": {name: -by_id[name]["onset"] for name in ids},
    }
    reach = {}
    for name in ids:
        seen, todo = set(), list(adjacency[name])
        while todo:
            nxt = todo.pop()
            if nxt in seen:
                continue
            seen.add(nxt)
            todo.extend(adjacency[nxt])
        reach[name] = seen
    raw["topology"] = {name: float(len(reach[name])) for name in ids}
    normalized = {mod: ranks(values) for mod, values in raw.items()}
    arms = {}
    for arm, modalities in ARMS.items():
        scores = {name: sum(normalized[m][name] for m in modalities) / len(modalities) for name in ids}
        ranking = sorted(ids, key=lambda name: (-scores[name], name))
        best, second = scores[ranking[0]], scores[ranking[1]]
        abstain = best - second < 0.05
        path = []
        if ranking[0] in reach and reach[ranking[0]]:
            endpoint = max(reach[ranking[0]], key=lambda name: (by_id[name]["neural_signal"], name))
            path = [ranking[0], endpoint]
        arms[arm] = {"ranking": ranking, "scores": scores, "abstained": abstain, "explanation_path": path}
    return {"scenario_id": case["scenario_id"], "arms": arms}


def main() -> None:
    cases = json.loads(INPUT.read_text(encoding="utf-8"))["cases"]
    predictions = [predict(case) for case in cases]
    RUN.mkdir(parents=True, exist_ok=True)
    out = RUN / "predictions.json"
    out.write_text(json.dumps({"predictions": predictions}, indent=2) + "\n", encoding="utf-8")
    seal = {"prediction_sha256": sha(out), "input_sha256": sha(INPUT), "labels_loaded": False, "network_used": False, "device": "cpu", "python": sys.version, "platform": platform.platform(), "numpy": np.__version__}
    (RUN / "prediction-seal.json").write_text(json.dumps(seal, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"predictions": len(predictions), "arms": list(ARMS), "sealed": True, "labels_loaded": False}, indent=2))


if __name__ == "__main__":
    main()
