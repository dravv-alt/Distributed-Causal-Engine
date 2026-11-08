from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np

BASE = Path(__file__).resolve().parents[1]
RUN = BASE / "results" / "E017-R001"
METHODS = ["neural_only", "symbolic_only", "neural_topology", "neural_topology_temporal", "full_fusion"]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    prediction_file = RUN / "predictions.json"
    seal = json.loads((RUN / "prediction-seal.json").read_text())
    assert sha(prediction_file) == seal["prediction_sha256"]
    assert seal["labels_loaded"] is False
    rows = json.loads(prediction_file.read_text())["predictions"]
    labels = json.loads((BASE / "fixtures/evaluator-only/test-labels.json").read_text())["case_labels"]
    published = json.loads((RUN / "evaluation.json").read_text())
    assert len(rows) == 600 and set(labels) == {r["scenario_id"] for r in rows}
    recomputed = {}
    for method in METHODS:
        hits1 = hits3 = abstain = explained = path_correct = 0
        reciprocal = []
        false = 0
        for row in rows:
            arm = row["arms"][method]
            target = labels[row["scenario_id"]]
            rank = arm["ranking"].index(target["root"]) + 1
            hit1, hit3 = rank == 1, rank <= 3
            hits1 += hit1; hits3 += hit3; abstain += arm["abstained"]
            false += (not hit1) and (not arm["abstained"])
            reciprocal.append(1.0 / rank)
            path = arm["explanation_path"]
            explained += bool(path)
            path_correct += bool(path and path[0] == target["root"] and path[1] in target["affected_descendants"])
        n = len(rows); covered = n - abstain
        recomputed[method] = {"top1": hits1/n, "top3": hits3/n, "mrr": float(np.mean(reciprocal)), "false_diagnosis_rate_nonabstained": false/covered if covered else None, "abstention_rate": abstain/n, "coverage": covered/n, "explanation_coverage": explained/n, "path_accuracy_among_cases": path_correct/n}
        for key, value in recomputed[method].items():
            assert abs(published["metrics"][method][key] - value) < 1e-12, (method, key, value, published["metrics"][method][key])
    independent_top1 = {name: recomputed[name]["top1"] for name in ("neural_only", "symbolic_only")}
    strongest = max(independent_top1, key=independent_top1.get)
    assert published["paired_full_fusion_vs_strongest_independent"]["baseline_arm"] == strongest
    assert abs(published["paired_full_fusion_vs_strongest_independent"]["top1_difference_full_minus_baseline"] - (recomputed["full_fusion"]["top1"] - recomputed[strongest]["top1"])) < 1e-12
    audit = {"audit": "E017-R001 independent evaluator recomputation", "passed": True, "cases": len(rows), "arms_recomputed": METHODS, "checks": ["prediction seal", "prediction/label coverage", "Top-1/Top-3/MRR", "false diagnosis", "abstention and coverage", "explanation coverage", "path accuracy", "strongest independent baseline and paired delta"], "hashes": {"predictions": sha(prediction_file), "labels": sha(BASE / "fixtures/evaluator-only/test-labels.json"), "evaluation": sha(RUN / "evaluation.json")}}
    (RUN / "independent-audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__": main()
