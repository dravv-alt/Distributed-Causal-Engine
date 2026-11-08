import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "E013_multiple_root_pilot"
OUT = BASE / "results" / "E013-R001"
fixture = json.loads((BASE / "fixtures/inference.json").read_text(encoding="utf-8"))
labels_path = BASE / "fixtures/evaluator-labels.json"
labels = json.loads(labels_path.read_text(encoding="utf-8"))["root_sets"]
pred_path = OUT / "predictions.json"
predictions = json.loads(pred_path.read_text(encoding="utf-8"))
stored = json.loads((OUT / "evaluation.json").read_text(encoding="utf-8"))
seal = json.loads((OUT / "prediction-seal.json").read_text(encoding="utf-8"))
methods = ("single_root_v1", "root_set_threshold_2_v1")
diffs = []
stats = {m: {"exact": 0, "collapse": 0, "ambiguous": 0, "single_ambiguous": 0, "empty": 0, "size": 0} for m in methods}

for case, row in zip(fixture["cases"], predictions, strict=True):
    for method in methods:
        support = case["support"]
        counts = {name: len(refs) for name, refs in support.items()}
        if method == "single_root_v1":
            peak = max(counts.values())
            leaders = [name for name, count in counts.items() if count == peak]
            predicted = [leaders[0]] if peak > 0 and len(leaders) == 1 else []
        else:
            predicted = sorted(name for name, count in counts.items() if count >= 2)
        observed = row["methods"][method]["selected_roots"]
        if predicted != observed:
            diffs.append(f"{case['case_id']}:{method}")
        truth = labels[case["case_id"]]
        stats[method]["exact"] += set(predicted) == set(truth)
        stats[method]["collapse"] += len(truth) > 1 and len(predicted) < 2
        stats[method]["ambiguous"] += len(predicted) > 1
        stats[method]["single_ambiguous"] += case["case_id"].startswith("S") and len(predicted) > 1
        stats[method]["empty"] += len(predicted) == 0
        stats[method]["size"] += len(predicted)

expected = {}
for method in methods:
    s = stats[method]
    expected[method] = {
        "exact_root_sets": s["exact"],
        "exact_root_set_rate": s["exact"] / len(predictions),
        "multi_root_collapse_count": s["collapse"],
        "multi_root_collapse_rate": s["collapse"] / 3,
        "ambiguous_cases": s["ambiguous"],
        "single_root_control_ambiguous_cases": s["single_ambiguous"],
        "empty_sets": s["empty"],
        "mean_predicted_set_size": s["size"] / len(predictions),
    }
stored_metrics_match = expected == stored["method_metrics"]
seal_match = hashlib.sha256(pred_path.read_bytes()).hexdigest() == seal["predictions_sha256"]
label_match = hashlib.sha256(labels_path.read_bytes()).hexdigest() == stored["label_hash"]
passed = not diffs and stored_metrics_match and seal_match and label_match
audit = {
    "run_id": "E013-R001",
    "status": "PASS" if passed else "FAIL",
    "prediction_differences": diffs,
    "all_metrics_match": stored_metrics_match,
    "prediction_seal_matches": seal_match,
    "label_hash_matches": label_match,
}
(OUT / "independent-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
print(json.dumps(audit, indent=2))
if not passed:
    raise SystemExit(1)
