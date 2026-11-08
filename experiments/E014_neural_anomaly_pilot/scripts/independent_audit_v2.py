from __future__ import annotations

import hashlib
import json
from pathlib import Path

import polars as pl
from sklearn.metrics import roc_auc_score

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "E014_neural_anomaly_pilot"
DATA = ROOT / "data" / "rcaeval"
OUT = BASE / "results" / "E014-R001"
METHODS = {
    "robust_max_z_v1": ("statistical_score", "statistical_alarm", "statistical"),
    "pytorch_autoencoder_v1": ("neural_score", "neural_alarm", "neural"),
}


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def independent_case_map() -> dict[str, str]:
    sample = json.loads((DATA / "evaluator-only" / "sample-selection-2026-11-07.json").read_text(encoding="utf-8"))
    mapping = {item["blind_case_id"]: item["source_case_name"] for item in sample["samples"]}
    selected = json.loads((DATA / "evaluator-only" / "selection-manifest.json").read_text(encoding="utf-8"))
    mapping[selected["selected_case_blind_id"]] = selected["selected_case_name"]
    return mapping


def summarize(labels: list[bool], scores: list[float], flags: list[bool]) -> dict:
    tp = fp = fn = tn = 0
    for actual, score_alarm in zip(labels, flags):
        if actual and score_alarm:
            tp += 1
        elif actual:
            fn += 1
        elif score_alarm:
            fp += 1
        else:
            tn += 1
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "precision": precision,
        "recall": recall,
        "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.0,
        "false_positive_rate": fp / (fp + tn) if fp + tn else None,
        "auroc": float(roc_auc_score(labels, scores)) if len(set(labels)) == 2 else None,
    }


def main() -> None:
    predictions_path = OUT / "predictions.jsonl"
    seal = json.loads((OUT / "prediction-seal.json").read_text(encoding="utf-8"))
    if sha(predictions_path) != seal["predictions_sha256"]:
        raise SystemExit("Prediction file differs from its seal")
    predictions = [json.loads(line) for line in predictions_path.read_text(encoding="utf-8").splitlines() if line]
    predictions_by_case = {}
    for row in predictions:
        predictions_by_case.setdefault(row["case_id"], []).append(row)
    mapping = independent_case_map()
    index_path = DATA / "evaluator-only" / "index-afeacb1" / "cases.parquet"
    index = {row["case"]: row for row in pl.read_parquet(index_path).to_dicts()}
    all_y = {name: [] for name in METHODS}
    all_scores = {name: [] for name in METHODS}
    all_flags = {name: [] for name in METHODS}
    rebuilt_cases = []
    rebuilt_alignment = []

    # Iterate the inference seal order, not evaluator-table order.
    for rel_path in seal["inference_input_hashes"]:
        blind_id = Path(rel_path).parent.name
        source_case = mapping[blind_id]
        label_row = index[source_case]
        telemetry = pl.read_parquet(DATA / "inference" / blind_id / "metrics.parquet")
        full_times = [int(x) for x in telemetry.get_column("time").to_list()]
        total_fault_rows = sum(value >= int(label_row["inject_time"]) for value in full_times)
        if total_fault_rows != int(label_row["faulty_timesteps"]):
            raise SystemExit(f"Evaluator-to-telemetry mismatch for {blind_id}")
        rebuilt_alignment.append({"blind_case_id": blind_id, "rows": len(full_times), "indexed_faulty_rows": total_fault_rows})
        case_rows = predictions_by_case[blind_id]
        y = [int(item["time"]) >= int(label_row["inject_time"]) for item in case_rows]
        report = {
            "blind_case_id": blind_id,
            "score_rows": len(case_rows),
            "fault_rows_in_score_suffix": sum(y),
            "indexed_fault_rows_total": total_fault_rows,
        }
        for method, (score_key, alarm_key, prefix) in METHODS.items():
            scores = [float(item[score_key]) for item in case_rows]
            alarms = [bool(item[alarm_key]) for item in case_rows]
            all_y[method].extend(y)
            all_scores[method].extend(scores)
            all_flags[method].extend(alarms)
            onset_rows = [item["row_index"] for item, fault in zip(case_rows, y) if fault]
            detected_rows = [item["row_index"] for item, fault, alarm in zip(case_rows, y, alarms) if fault and alarm]
            onset = min(onset_rows) if onset_rows else None
            first_hit = min(detected_rows) if detected_rows else None
            report[prefix] = {
                "fault_event_detected": first_hit is not None,
                "detection_delay_timesteps": first_hit - onset if first_hit is not None and onset is not None else None,
                "false_positive_rows": sum(alarm and not fault for alarm, fault in zip(alarms, y)),
            }
        rebuilt_cases.append(report)

    metrics = {}
    for method, (_, _, prefix) in METHODS.items():
        metrics[method] = summarize(all_y[method], all_scores[method], all_flags[method])
        faulty_cases = [case for case in rebuilt_cases if case["fault_rows_in_score_suffix"] > 0]
        hits = sum(case[prefix]["fault_event_detected"] for case in faulty_cases)
        delays = [case[prefix]["detection_delay_timesteps"] for case in faulty_cases if case[prefix]["detection_delay_timesteps"] is not None]
        metrics[method]["fault_case_detection_rate"] = hits / len(faulty_cases) if faulty_cases else None
        metrics[method]["fault_case_count"] = len(faulty_cases)
        metrics[method]["mean_detection_delay_timesteps"] = sum(delays) / len(delays) if delays else None

    stored = json.loads((OUT / "evaluation.json").read_text(encoding="utf-8"))
    aggregate_match = metrics == stored["method_metrics"]
    per_case_match = rebuilt_cases == stored["case_metrics"]
    alignment_match = rebuilt_alignment == stored["evaluator_label_alignment"]
    index_match = sha(index_path) == stored["evaluator_index_sha256"]
    passed = aggregate_match and per_case_match and alignment_match and index_match
    result = {
        "run_id": "E014-R001",
        "status": "PASS" if passed else "FAIL",
        "aggregate_metrics_match": aggregate_match,
        "per_case_metrics_match": per_case_match,
        "label_alignment_match": alignment_match,
        "evaluator_index_hash_matches": index_match,
        "prediction_seal_matches": sha(predictions_path) == seal["predictions_sha256"],
    }
    (OUT / "independent-audit-v2.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
