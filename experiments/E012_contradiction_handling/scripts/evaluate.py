from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "E012_contradiction_handling"
OUT = BASE / "results" / "E012-R001"


def main() -> None:
    predictions_path = OUT / "predictions.json"
    seal = json.loads((OUT / "prediction-seal.json").read_text(encoding="utf-8"))
    if hashlib.sha256(predictions_path.read_bytes()).hexdigest() != seal["predictions_sha256"]:
        raise SystemExit("prediction hash does not match seal")
    if seal["evaluator_labels_opened"]:
        raise SystemExit("invalid pre-evaluation seal")
    labels_path = BASE / "fixtures" / "evaluator-labels.json"
    labels = json.loads(labels_path.read_text(encoding="utf-8"))["case_roots"]
    predictions = json.loads(predictions_path.read_text(encoding="utf-8"))
    methods = ("support_only_v1", "contradiction_aware_v1")
    summary = {}
    for method in methods:
        exact = abstentions = false_diagnoses = 0
        for row in predictions:
            selected = row["methods"][method]["selected"]
            truth = labels[row["case_id"]]
            exact += selected == truth
            abstentions += selected is None
            false_diagnoses += selected is not None and selected != truth
        summary[method] = {
            "exact_root_correct": exact,
            "exact_root_rate": exact / len(predictions),
            "abstentions": abstentions,
            "abstention_rate": abstentions / len(predictions),
            "false_diagnoses": false_diagnoses,
        }
    contradicted_cases = []
    for row in predictions:
        aware = row["methods"]["contradiction_aware_v1"]
        if any(value["contradiction"] for value in aware["evidence"].values()):
            contradicted_cases.append(row)
    rejected = sum(
        not any(
            candidate == row["methods"]["contradiction_aware_v1"]["selected"]
            and evidence["contradiction"]
            for candidate, evidence in row["methods"]["contradiction_aware_v1"]["evidence"].items()
        )
        for row in contradicted_cases
    )
    evaluation = {
        "run_id": "E012-R001",
        "case_count": len(predictions),
        "method_metrics": summary,
        "contradicted_candidate_cases": len(contradicted_cases),
        "contradicted_candidate_rejections": rejected,
        "contradicted_candidate_rejection_rate": rejected / len(contradicted_cases) if contradicted_cases else None,
        "label_hash": hashlib.sha256(labels_path.read_bytes()).hexdigest(),
        "root_labels_written": False,
    }
    (OUT / "evaluation.json").write_text(json.dumps(evaluation, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(evaluation, indent=2))


if __name__ == "__main__":
    main()
