"""Second independent pass covering every reported E012 aggregate."""
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "E012_contradiction_handling"
OUT = BASE / "results" / "E012-R001"

pred_path = OUT / "predictions.json"
seal = json.loads((OUT / "prediction-seal.json").read_text(encoding="utf-8"))
predictions = json.loads(pred_path.read_text(encoding="utf-8"))
labels_path = BASE / "fixtures" / "evaluator-labels.json"
labels = json.loads(labels_path.read_text(encoding="utf-8"))["case_roots"]
fixture = json.loads((BASE / "fixtures" / "inference.json").read_text(encoding="utf-8"))
stored = json.loads((OUT / "evaluation.json").read_text(encoding="utf-8"))
methods = ("support_only_v1", "contradiction_aware_v1")
metrics = {name: {"exact": 0, "abstentions": 0, "false_diagnoses": 0} for name in methods}
contradicted_count = rejected_count = 0
ranking_differences = []

for case, row in zip(fixture["cases"], predictions, strict=True):
    for name in methods:
        scores = {
            candidate: len(case["support"][candidate]) - (len(case["contradiction"][candidate]) if name == "contradiction_aware_v1" else 0)
            for candidate in case["candidates"]
        }
        best = max(scores.values())
        winners = [candidate for candidate, score in scores.items() if score == best]
        selected = winners[0] if best > 0 and len(winners) == 1 else None
        observed = row["methods"][name]
        if selected != observed["selected"] or scores != observed["scores"]:
            ranking_differences.append(f"{case['case_id']}:{name}")
        root = labels[case["case_id"]]
        metrics[name]["exact"] += selected == root
        metrics[name]["abstentions"] += selected is None
        metrics[name]["false_diagnoses"] += selected is not None and selected != root
    has_contradiction = any(case["contradiction"].values())
    if has_contradiction:
        contradicted_count += 1
        selected = row["methods"]["contradiction_aware_v1"]["selected"]
        contradicted_candidates = {candidate for candidate, refs in case["contradiction"].items() if refs}
        rejected_count += selected not in contradicted_candidates

expected_matches = {}
for name in methods:
    n = len(predictions)
    expected_matches[name] = {
        "exact_root_correct": metrics[name]["exact"],
        "exact_root_rate": metrics[name]["exact"] / n,
        "abstentions": metrics[name]["abstentions"],
        "abstention_rate": metrics[name]["abstentions"] / n,
        "false_diagnoses": metrics[name]["false_diagnoses"],
    }
stored_matches = expected_matches == stored["method_metrics"]
rejection_matches = (
    contradicted_count == stored["contradicted_candidate_cases"]
    and rejected_count == stored["contradicted_candidate_rejections"]
    and rejected_count / contradicted_count == stored["contradicted_candidate_rejection_rate"]
)
seal_matches = hashlib.sha256(pred_path.read_bytes()).hexdigest() == seal["predictions_sha256"]
label_hash_matches = hashlib.sha256(labels_path.read_bytes()).hexdigest() == stored["label_hash"]
passed = not ranking_differences and stored_matches and rejection_matches and seal_matches and label_hash_matches
audit = {
    "run_id": "E012-R001",
    "status": "PASS" if passed else "FAIL",
    "ranking_differences": ranking_differences,
    "all_method_metrics_match": stored_matches,
    "contradiction_rejection_metrics_match": rejection_matches,
    "prediction_seal_matches": seal_matches,
    "label_hash_matches": label_hash_matches,
    "evaluator_root_accessed": True,
}
(OUT / "independent-audit-v2.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
print(json.dumps(audit, indent=2))
if not passed:
    raise SystemExit(1)
