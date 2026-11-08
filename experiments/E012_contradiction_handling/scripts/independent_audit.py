from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "E012_contradiction_handling"
OUT = BASE / "results" / "E012-R001"


def independent_scores(case: dict, method: str) -> dict:
    scores = {}
    for candidate in case["candidates"]:
        score = len(case["support"][candidate])
        if method == "contradiction_aware_v1":
            score -= len(case["contradiction"][candidate])
        scores[candidate] = score
    best = max(scores.values())
    leaders = [name for name in scores if scores[name] == best]
    selected = leaders[0] if best > 0 and len(leaders) == 1 else None
    return {"selected": selected, "scores": scores}


def main() -> None:
    fixture = json.loads((BASE / "fixtures/inference.json").read_text(encoding="utf-8"))
    labels_path = BASE / "fixtures/evaluator-labels.json"
    labels = json.loads(labels_path.read_text(encoding="utf-8"))["case_roots"]
    predictions_path = OUT / "predictions.json"
    predictions = json.loads(predictions_path.read_text(encoding="utf-8"))
    if hashlib.sha256(predictions_path.read_bytes()).hexdigest() != json.loads((OUT / "prediction-seal.json").read_text(encoding="utf-8"))["predictions_sha256"]:
        raise SystemExit("prediction seal mismatch")
    diff = []
    expected_metrics = {m: {"exact": 0, "abstain": 0, "false": 0} for m in ("support_only_v1", "contradiction_aware_v1")}
    contradicted = rejected = 0
    for case, row in zip(fixture["cases"], predictions, strict=True):
        if row["case_id"] != case["case_id"]:
            diff.append(case["case_id"])
            continue
        truth = labels[case["case_id"]]
        for method in expected_metrics:
            recalc = independent_scores(case, method)
            actual = row["methods"][method]
            if actual["selected"] != recalc["selected"] or actual["scores"] != recalc["scores"]:
                diff.append(f"{case['case_id']}:{method}")
            selected = recalc["selected"]
            expected_metrics[method]["exact"] += selected == truth
            expected_metrics[method]["abstain"] += selected is None
            expected_metrics[method]["false"] += selected is not None and selected != truth
        aware = row["methods"]["contradiction_aware_v1"]
        if any(case["contradiction"].values()):
            contradicted += 1
            if aware["selected"] not in {c for c, refs in case["contradiction"].items() if refs}:
                rejected += 1
    stored = json.loads((OUT / "evaluation.json").read_text(encoding="utf-8"))
    expected_exact = {m: values["exact"] for m, values in expected_metrics.items()}
    stored_exact = {m: values["exact_root_correct"] for m, values in stored["method_metrics"].items()}
    passed = not diff and expected_exact == stored_exact and contradicted == stored["contradicted_candidate_cases"] and rejected == stored["contradicted_candidate_rejections"]
    audit = {
        "run_id": "E012-R001",
        "status": "PASS" if passed else "FAIL",
        "prediction_recomputation_differences": diff,
        "recomputed_counts": expected_metrics,
        "stored_exact_counts_match": expected_exact == stored_exact,
        "contradicted_case_count_match": contradicted == stored["contradicted_candidate_cases"],
        "contradiction_rejection_count_match": rejected == stored["contradicted_candidate_rejections"],
        "label_hash": hashlib.sha256(labels_path.read_bytes()).hexdigest(),
    }
    (OUT / "independent-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
