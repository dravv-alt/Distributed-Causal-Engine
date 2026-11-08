from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "E013_multiple_root_pilot"
OUT = BASE / "results" / "E013-R001"
METHODS = ("single_root_v1", "root_set_threshold_2_v1")


def main() -> None:
    pred_path = OUT / "predictions.json"
    seal = json.loads((OUT / "prediction-seal.json").read_text(encoding="utf-8"))
    if hashlib.sha256(pred_path.read_bytes()).hexdigest() != seal["predictions_sha256"]:
        raise SystemExit("prediction seal mismatch")
    if seal["evaluator_labels_opened"]:
        raise SystemExit("invalid seal state")
    labels_path = BASE / "fixtures" / "evaluator-labels.json"
    roots = json.loads(labels_path.read_text(encoding="utf-8"))["root_sets"]
    rows = json.loads(pred_path.read_text(encoding="utf-8"))
    methods = {}
    for method in METHODS:
        exact = collapse = ambiguous = 0
        sizes = []
        for row in rows:
            predicted = row["methods"][method]["selected_roots"]
            truth = roots[row["case_id"]]
            exact += set(predicted) == set(truth)
            sizes.append(len(predicted))
            ambiguous += len(predicted) > 1
            if len(truth) > 1:
                collapse += len(predicted) < 2
        single_ambiguous = sum(len(row["methods"][method]["selected_roots"]) > 1 for row in rows if row["case_id"].startswith("S"))
        methods[method] = {
            "exact_root_sets": exact,
            "exact_root_set_rate": exact / len(rows),
            "multi_root_collapse_count": collapse,
            "multi_root_collapse_rate": collapse / 3,
            "ambiguous_cases": ambiguous,
            "single_root_control_ambiguous_cases": single_ambiguous,
            "empty_sets": sum(size == 0 for size in sizes),
            "mean_predicted_set_size": sum(sizes) / len(sizes),
        }
    result = {
        "run_id": "E013-R001",
        "case_count": len(rows),
        "multi_root_case_count": 3,
        "single_root_control_count": 3,
        "method_metrics": methods,
        "label_hash": hashlib.sha256(labels_path.read_bytes()).hexdigest(),
        "root_labels_written": False,
    }
    (OUT / "evaluation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
