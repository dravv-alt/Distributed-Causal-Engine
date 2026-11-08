from __future__ import annotations

import hashlib
import json
from pathlib import Path

import polars as pl
from sklearn.metrics import roc_auc_score


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "E014_neural_anomaly_pilot"
OUT = BASE / "results" / "E014-R001"
DATA = ROOT / "data" / "rcaeval"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def case_map() -> dict[str, str]:
    mapping = {}
    selection = json.loads((DATA / "evaluator-only" / "sample-selection-2026-11-07.json").read_text(encoding="utf-8"))
    for item in selection["samples"]:
        mapping[item["blind_case_id"]] = item["source_case_name"]
    single = json.loads((DATA / "evaluator-only" / "selection-manifest.json").read_text(encoding="utf-8"))
    mapping[single["selected_case_blind_id"]] = single["selected_case_name"]
    return mapping


def metric_summary(y: list[bool], scores: list[float], alarms: list[bool]) -> dict:
    tp = sum(a and t for a, t in zip(alarms, y))
    fp = sum(a and not t for a, t in zip(alarms, y))
    fn = sum((not a) and t for a, t in zip(alarms, y))
    tn = sum((not a) and (not t) for a, t in zip(alarms, y))
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
        "auroc": float(roc_auc_score(y, scores)) if len(set(y)) == 2 else None,
    }


def main() -> None:
    pred_path = OUT / "predictions.jsonl"
    seal = json.loads((OUT / "prediction-seal.json").read_text(encoding="utf-8"))
    if sha(pred_path) != seal["predictions_sha256"]:
        raise SystemExit("prediction file does not match its pre-evaluation seal")
    if seal["labels_opened"]:
        raise SystemExit("invalid seal state")

    mapping = case_map()
    index_path = DATA / "evaluator-only" / "index-afeacb1" / "cases.parquet"
    index = pl.read_parquet(index_path)
    index_by_case = {row["case"]: row for row in index.to_dicts()}
    score_rows = [json.loads(line) for line in pred_path.read_text(encoding="utf-8").splitlines() if line]
    grouped = {}
    for row in score_rows:
        grouped.setdefault(row["case_id"], []).append(row)

    evaluated: dict[str, list[dict]] = {"robust_max_z_v1": [], "pytorch_autoencoder_v1": []}
    case_reports = []
    label_alignment = []
    for blind_id in seal["inference_input_hashes"]:
        blind_id = Path(blind_id).parent.name
        source_case = mapping[blind_id]
        label = index_by_case[source_case]
        metric = pl.read_parquet(DATA / "inference" / blind_id / "metrics.parquet")
        times = [int(v) for v in metric.get_column("time").to_list()]
        actual_faulty = sum(t >= int(label["inject_time"]) for t in times)
        if actual_faulty != int(label["faulty_timesteps"]):
            raise SystemExit(f"Evaluator label alignment mismatch for {blind_id}: {actual_faulty} != indexed {label['faulty_timesteps']}")
        label_alignment.append({"blind_case_id": blind_id, "rows": len(times), "indexed_faulty_rows": actual_faulty})
        rows = grouped[blind_id]
        y = [int(row["time"]) >= int(label["inject_time"]) for row in rows]
        case_summary = {"blind_case_id": blind_id, "score_rows": len(rows), "fault_rows_in_score_suffix": sum(y), "indexed_fault_rows_total": actual_faulty}
        for method, score_key, alarm_key, metric_key in (
            ("robust_max_z_v1", "statistical_score", "statistical_alarm", "statistical"),
            ("pytorch_autoencoder_v1", "neural_score", "neural_alarm", "neural"),
        ):
            scores = [float(row[score_key]) for row in rows]
            alarms = [bool(row[alarm_key]) for row in rows]
            evaluated[method].append({"y": y, "scores": scores, "alarms": alarms})
            first_fault = next((int(row["row_index"]) for row, is_fault in zip(rows, y) if is_fault), None)
            first_detection = next((int(row["row_index"]) for row, is_fault, alarm in zip(rows, y, alarms) if is_fault and alarm), None)
            case_summary[metric_key] = {
                "fault_event_detected": first_detection is not None,
                "detection_delay_timesteps": first_detection - first_fault if first_detection is not None and first_fault is not None else None,
                "false_positive_rows": sum(alarm and not is_fault for alarm, is_fault in zip(alarms, y)),
            }
        case_reports.append(case_summary)

    method_metrics = {}
    for method, values in evaluated.items():
        case_metric_key = "statistical" if method == "robust_max_z_v1" else "neural"
        y = [v for case in values for v in case["y"]]
        scores = [v for case in values for v in case["scores"]]
        alarms = [v for case in values for v in case["alarms"]]
        method_metrics[method] = metric_summary(y, scores, alarms)
        event_rows = [case[case_metric_key]["fault_event_detected"] for case in case_reports if case["fault_rows_in_score_suffix"] > 0]
        method_metrics[method]["fault_case_detection_rate"] = sum(event_rows) / len(event_rows) if event_rows else None
        method_metrics[method]["fault_case_count"] = len(event_rows)
        method_metrics[method]["mean_detection_delay_timesteps"] = (
            sum(case[case_metric_key]["detection_delay_timesteps"] for case in case_reports if case["fault_rows_in_score_suffix"] > 0 and case[case_metric_key]["detection_delay_timesteps"] is not None)
            / sum(case[case_metric_key]["detection_delay_timesteps"] is not None for case in case_reports if case["fault_rows_in_score_suffix"] > 0)
            if any(case["fault_rows_in_score_suffix"] > 0 and case[case_metric_key]["detection_delay_timesteps"] is not None for case in case_reports) else None
        )
    result = {
        "run_id": "E014-R001",
        "scope": "within-case chronological suffix detection; not held-out incident evaluation",
        "case_count": len(case_reports),
        "method_metrics": method_metrics,
        "case_metrics": case_reports,
        "evaluator_label_alignment": label_alignment,
        "evaluator_index_sha256": sha(index_path),
        "mapping_manifest_hashes": {
            "sample_selection": sha(DATA / "evaluator-only" / "sample-selection-2026-11-07.json"),
            "re2tt_selection": sha(DATA / "evaluator-only" / "selection-manifest.json"),
        },
        "labels_written": False,
    }
    (OUT / "evaluation.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": result["run_id"], "method_metrics": method_metrics, "case_count": len(case_reports), "evaluator_alignment_rows": sum(x["rows"] for x in label_alignment)}, indent=2))


if __name__ == "__main__":
    main()
