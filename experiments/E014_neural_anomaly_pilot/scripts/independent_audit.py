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


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def derive_mapping() -> dict[str, str]:
    mapping = {}
    sample = json.loads((DATA / "evaluator-only" / "sample-selection-2026-11-07.json").read_text(encoding="utf-8"))
    for item in sample["samples"]:
        mapping[item["blind_case_id"]] = item["source_case_name"]
    single = json.loads((DATA / "evaluator-only" / "selection-manifest.json").read_text(encoding="utf-8"))
    mapping[single["selected_case_blind_id"]] = single["selected_case_name"]
    return mapping


def count_metrics(labels: list[bool], scores: list[float], alarms: list[bool]) -> dict:
    tp = sum(bool(p and y) for p, y in zip(alarms, labels))
    fp = sum(bool(p and not y) for p, y in zip(alarms, labels))
    fn = sum(bool(not p and y) for p, y in zip(alarms, labels))
    tn = sum(bool(not p and not y) for p, y in zip(alarms, labels))
    precision = tp / (tp + fp) if tp + fp else 0.0
    recall = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    auc = float(roc_auc_score(labels, scores)) if len(set(labels)) == 2 else None
    return {
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "false_positive_rate": fp / (fp + tn) if fp + tn else None,
        "auroc": auc,
    }


def main() -> None:
    pred_path = OUT / "predictions.jsonl"
    seal = json.loads((OUT / "prediction-seal.json").read_text(encoding="utf-8"))
    if digest(pred_path) != seal["predictions_sha256"]:
        raise SystemExit("Prediction seal mismatch")
    records = [json.loads(line) for line in pred_path.read_text(encoding="utf-8").splitlines() if line]
    grouped = {}
    for record in records:
        grouped.setdefault(record["case_id"], []).append(record)
    mapping = derive_mapping()
    index_file = DATA / "evaluator-only" / "index-afeacb1" / "cases.parquet"
    idx = {row["case"]: row for row in pl.read_parquet(index_file).to_dicts()}
    all_labels = {method: [] for method in METHODS}
    all_scores = {method: [] for method in METHODS}
    all_alarms = {method: [] for method in METHODS}
    case_metrics = []
    label_rows = []
    for blind_id, source_name in mapping.items():
        record_rows = grouped[blind_id]
        label = idx[source_name]
        full_time = pl.read_parquet(DATA / "inference" / blind_id / "metrics.parquet").get_column("time").to_list()
        actual_fault_rows = sum(int(t) >= int(label["inject_time"]) for t in full_time)
        if actual_fault_rows != int(label["faulty_timesteps"]):
            raise SystemExit(f"Index-to-telemetry alignment mismatch for {blind_id}")
        label_rows.append({"blind_case_id": blind_id, "rows": len(full_time), "fault_rows": actual_fault_rows})
        y = [int(record["time"]) >= int(label["inject_time"]) for record in record_rows]
        case = {"blind_case_id": blind_id, "score_rows": len(y), "fault_rows_in_score_suffix": sum(y)}
        for method, (score_key, alarm_key, prefix) in METHODS.items():
            scores = [float(record[score_key]) for record in record_rows]
            alarms = [bool(record[alarm_key]) for record in record_rows]
            all_labels[method].extend(y)
            all_scores[method].extend(scores)
            all_alarms[method].extend(alarms)
            onsets = [int(record["row_index"]) for record, flag in zip(record_rows, y) if flag]
            hits = [int(record["row_index"]) for record, flag, alarm in zip(record_rows, y, alarms) if flag and alarm]
            first_onset = min(onsets) if onsets else None
            first_hit = min(hits) if hits else None
            case[prefix] = {
                "fault_event_detected": first_hit is not None,
                "detection_delay_timesteps": first_hit - first_onset if first_hit is not None and first_onset is not None else None,
                "false_positive_rows": sum(alarm and not fault for alarm, fault in zip(alarms, y)),
            }
        case_metrics.append(case)
    aggregate = {method: count_metrics(all_labels[method], all_scores[method], all_alarms[method]) for method in METHODS}
    for method, (_, _, prefix) in METHODS.items():
        fault_cases = [case for case in case_metrics if case["fault_rows_in_score_suffix"] > 0]
        detected = sum(case[prefix]["fault_event_detected"] for case in fault_cases)
        delays = [case[prefix]["detection_delay_timesteps"] for case in fault_cases if case[prefix]["detection_delay_timesteps"] is not None]
        aggregate[method]["fault_case_detection_rate"] = detected / len(fault_cases) if fault_cases else None
        aggregate[method]["fault_case_count"] = len(fault_cases)
        aggregate[method]["mean_detection_delay_timesteps"] = sum(delays) / len(delays) if delays else None

    stored = json.loads((OUT / "evaluation.json").read_text(encoding="utf-8"))
    aggregate_match = aggregate == stored["method_metrics"]
    case_match = case_metrics == stored["case_metrics"]
    alignment_match = label_rows == stored["evaluator_label_alignment"]
    passed = aggregate_match and case_match and alignment_match
    audit = {
        "run_id": "E014-R001",
        "status": "PASS" if passed else "FAIL",
        "aggregate_metrics_match": aggregate_match,
        "per_case_metrics_match": case_match,
        "label_alignment_match": alignment_match,
        "prediction_hash_matches_seal": digest(pred_path) == seal["predictions_sha256"],
        "evaluator_index_hash_matches": digest(index_file) == stored["evaluator_index_sha256"],
    }
    (OUT / "independent-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
