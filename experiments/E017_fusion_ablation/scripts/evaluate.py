from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parents[1]
RUN = BASE / "results" / "E017-R001"
METHODS = ["neural_only", "symbolic_only", "neural_topology", "neural_topology_temporal", "full_fusion"]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def wilson(x: int, n: int) -> list[float | None]:
    if n == 0:
        return [None, None]
    z = 1.959963984540054
    p = x / n
    d = 1 + z * z / n
    center = (p + z * z / (2 * n)) / d
    half = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return [float(center - half), float(center + half)]


def metric(rows: list[dict], labels: dict, method: str) -> dict:
    top1 = top3 = false = abstain = explained = path_correct = 0
    reciprocal = []
    for row in rows:
        arm = row["arms"][method]
        truth = labels[row["scenario_id"]]
        ranking = arm["ranking"]
        rank = ranking.index(truth["root"]) + 1
        top1 += rank == 1
        top3 += rank <= 3
        abstain += arm["abstained"]
        reciprocal.append(1 / rank)
        false += (rank != 1) and (not arm["abstained"])
        path = arm["explanation_path"]
        explained += bool(path)
        path_correct += bool(path and path[0] == truth["root"] and path[1] in truth["affected_descendants"])
    n = len(rows)
    nonabstained = n - abstain
    return {
        "n": n,
        "top1": top1 / n,
        "top1_wilson95": wilson(top1, n),
        "top3": top3 / n,
        "mrr": float(np.mean(reciprocal)),
        "false_diagnosis_rate_nonabstained": false / nonabstained if nonabstained else None,
        "abstention_rate": abstain / n,
        "coverage": nonabstained / n,
        "explanation_coverage": explained / n,
        "path_accuracy_among_cases": path_correct / n,
        "path_accuracy_when_explained": path_correct / explained if explained else None,
    }


def main() -> None:
    pred_path = RUN / "predictions.json"
    seal = json.loads((RUN / "prediction-seal.json").read_text(encoding="utf-8"))
    if seal["prediction_sha256"] != sha(pred_path) or seal["labels_loaded"] is not False:
        raise SystemExit("prediction seal invalid")
    rows = json.loads(pred_path.read_text(encoding="utf-8"))["predictions"]
    label_path = BASE / "fixtures" / "evaluator-only" / "test-labels.json"
    labels = json.loads(label_path.read_text(encoding="utf-8"))["case_labels"]
    if set(labels) != {row["scenario_id"] for row in rows}:
        raise SystemExit("label/prediction coverage mismatch")
    metrics = {method: metric(rows, labels, method) for method in METHODS}
    independent = {name: metrics[name]["top1"] for name in ("neural_only", "symbolic_only")}
    strongest = max(independent, key=independent.get)
    y_full = np.asarray([r["arms"]["full_fusion"]["ranking"][0] == labels[r["scenario_id"]]["root"] for r in rows], dtype=np.int8)
    y_base = np.asarray([r["arms"][strongest]["ranking"][0] == labels[r["scenario_id"]]["root"] for r in rows], dtype=np.int8)
    rng = np.random.default_rng(17015)
    samples = rng.integers(0, len(rows), size=(10000, len(rows)))
    differences = (y_full[samples].mean(axis=1) - y_base[samples].mean(axis=1)).tolist()
    paired = {"baseline_arm": strongest, "top1_difference_full_minus_baseline": metrics["full_fusion"]["top1"] - metrics[strongest]["top1"], "bootstrap95_percentile": [float(np.quantile(differences, .025)), float(np.quantile(differences, .975))], "bootstrap_replicates": 10000, "seed": 17015}
    result = {"experiment": "E017-R001", "planning_stage": "XP014", "dataset": "synthetic generated fixtures", "n_cases": len(rows), "metrics": metrics, "paired_full_fusion_vs_strongest_independent": paired, "provenance": {"prediction_sha256": sha(pred_path), "test_input_sha256": sha(BASE / "fixtures" / "test-inputs.json"), "evaluator_label_sha256": sha(label_path)}, "interpretation": "Synthetic fusion behavior only; no real DCE or RCAEval fusion evidence."}
    out = RUN / "evaluation.json"
    out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
