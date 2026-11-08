"""Evaluator-only check that model fit/calibration partitions precede fault onset."""
import json
from pathlib import Path

import polars as pl


ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data" / "rcaeval"
OUT = ROOT / "experiments" / "E014_neural_anomaly_pilot" / "results" / "E014-R001"
selection = json.loads((DATA / "evaluator-only" / "sample-selection-2026-11-07.json").read_text(encoding="utf-8"))
mapping = {item["blind_case_id"]: item["source_case_name"] for item in selection["samples"]}
special = json.loads((DATA / "evaluator-only" / "selection-manifest.json").read_text(encoding="utf-8"))
mapping[special["selected_case_blind_id"]] = special["selected_case_name"]
index = {row["case"]: row for row in pl.read_parquet(DATA / "evaluator-only" / "index-afeacb1" / "cases.parquet").to_dicts()}
seal = json.loads((OUT / "prediction-seal.json").read_text(encoding="utf-8"))
results = []
for partition in seal["case_partitions"]:
    blind = partition["case_id"]
    label = index[mapping[blind]]
    times = pl.read_parquet(DATA / "inference" / blind / "metrics.parquet").get_column("time").to_list()
    fault_start = next((i for i, value in enumerate(times) if int(value) >= int(label["inject_time"])), len(times))
    calibration_end = partition["fit_rows"] + partition["calibration_rows"]
    normal_before_score = fault_start >= calibration_end
    results.append({
        "blind_case_id": blind,
        "fit_rows": partition["fit_rows"],
        "calibration_rows": partition["calibration_rows"],
        "score_start_row": calibration_end,
        "evaluator_fault_start_row": fault_start if fault_start < len(times) else None,
        "no_fault_rows_in_fit_or_calibration": normal_before_score,
    })
audit = {
    "run_id": "E014-R001",
    "evaluator_only": True,
    "case_count": len(results),
    "all_fit_and_calibration_rows_precede_fault": all(x["no_fault_rows_in_fit_or_calibration"] for x in results),
    "cases": results,
}
(OUT / "partition-label-audit.json").write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"case_count": audit["case_count"], "all_fit_and_calibration_rows_precede_fault": audit["all_fit_and_calibration_rows_precede_fault"]}, indent=2))
if not audit["all_fit_and_calibration_rows_precede_fault"]:
    raise SystemExit(1)
