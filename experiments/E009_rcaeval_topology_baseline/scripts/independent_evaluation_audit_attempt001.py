"""Recompute E009 label metrics independently after sealed inference."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "E009_rcaeval_topology_baseline"
RUN = EXP / "results" / "E009-R001"
CFG = json.loads((EXP / "configuration.json").read_text(encoding="utf-8"))
EVAL = ROOT / "data" / "rcaeval" / "evaluator-only"
MAP1 = EVAL / "selection-manifest.json"
MAP2 = EVAL / "sample-selection-2026-11-07.json"
INDEX = EVAL / "index-afeacb1" / "cases.parquet"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_new(path: Path, payload: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")


def credit(rows: list[dict], target: str, k: int) -> float:
    matches = [row["score"] for row in rows if row["service"] == target]
    if not matches:
        return 0.0
    score = matches[0]
    above = len([row for row in rows if row["score"] > score])
    tied = len([row for row in rows if row["score"] == score])
    return max(0.0, min(1.0, (k - above) / tied))


def mapping() -> dict[str, str]:
    one, many = json.loads(MAP1.read_text(encoding="utf-8")), json.loads(MAP2.read_text(encoding="utf-8"))
    out = {one["selected_case_blind_id"]: one["selected_case_name"]}
    out.update({item["blind_case_id"]: item["source_case_name"] for item in many["samples"]})
    if set(out) != set(CFG["blind_case_ids"]):
        raise ValueError("independent mapping does not match the preregistered population")
    return out


def main() -> None:
    seal = json.loads((RUN / "prediction-seal.json").read_text(encoding="utf-8"))
    predictions_path = RUN / "predictions.jsonl"
    if digest(predictions_path) != seal["prediction_sha256"]:
        raise ValueError("sealed predictions have changed")
    join = mapping()
    truth_rows = pl.read_parquet(INDEX, columns=["case", "root_cause_service"]).filter(
        pl.col("case").is_in(list(join.values()))).to_dicts()
    truth = {row["case"]: row["root_cause_service"] for row in truth_rows}
    if len(truth) != len(join) or len(truth_rows) != len(join):
        raise ValueError("independent exact case join failed")

    records = [json.loads(line) for line in predictions_path.read_text(encoding="utf-8").splitlines()]
    sums = {method: {key: 0.0 for key in ("top1_tie_aware", "top3_tie_aware",
                                          "top1_deterministic", "top3_deterministic",
                                          "top_score_set_exact_accuracy", "abstentions",
                                          "root_candidate_coverage", "root_explanation_coverage")}
            for method in CFG["methods"]}
    for record in records:
        target = truth[join[record["blind_case_id"]]]
        for method in CFG["methods"]:
            ranked = record["methods"][method]
            location = next((i for i, x in enumerate(ranked, 1) if x["service"] == target), None)
            best = max((x["score"] for x in ranked), default=None)
            best_set = {x["service"] for x in ranked if x["score"] == best} if best is not None else set()
            root_row = next((x for x in ranked if x["service"] == target), None)
            sums[method]["top1_tie_aware"] += credit(ranked, target, 1)
            sums[method]["top3_tie_aware"] += credit(ranked, target, 3)
            sums[method]["top1_deterministic"] += float(location == 1)
            sums[method]["top3_deterministic"] += float(location is not None and location <= 3)
            sums[method]["top_score_set_exact_accuracy"] += float(best_set == {target})
            sums[method]["abstentions"] += float(not ranked)
            sums[method]["root_candidate_coverage"] += float(root_row is not None)
            sums[method]["root_explanation_coverage"] += float(
                method == "topology_shared_callers_v1" and bool(root_row and root_row["reachable_callers"]))
    n = len(records)
    aggregates = {method: {key: value / n for key, value in cols.items()}
                  for method, cols in sums.items()}
    aggregates = {method: {"cases": n, **stats} for method, stats in aggregates.items()}
    saved = json.loads((RUN / "evaluation.json").read_text(encoding="utf-8"))
    key_metrics = list(sums["topology_shared_callers_v1"])
    metric_match = all(abs(aggregates[m][k] - saved["aggregate"][m][k]) < 1e-12
                       for m in CFG["methods"] for k in key_metrics)
    report = {"audit": "independent evaluator-side recomputation",
              "status": "PASS" if metric_match else "FAIL",
              "prediction_sha256": seal["prediction_sha256"],
              "case_join_count": len(truth), "case_result_count": len(records),
              "aggregates_recomputed": aggregates,
              "saved_aggregate_match": metric_match,
              "selection_and_label_index_hashes": {"selection_manifest": digest(MAP1),
                                                   "sample_selection": digest(MAP2),
                                                   "case_index": digest(INDEX)},
              "report_contains_root_service_labels": False}
    write_new(RUN / "independent-evaluation-audit.json", report)
    write_new(RUN / "post-prediction-source-manifest.json", {
        "mapping_recovery": "Evaluator attempt 1 stopped before label-index read because it used only the 8-case map. This retry combined the exact original one-case selection manifest with that 8-case map; scope and scoring unchanged.",
        "failed_evaluator_script_sha256": digest(EXP / "scripts" / "evaluate_labels.py"),
        "successful_evaluator_script_sha256": digest(EXP / "scripts" / "evaluate_labels_after_map_recovery.py"),
        "independent_audit_script_sha256": digest(Path(__file__)),
        "prediction_sha256": seal["prediction_sha256"],
        "mapping_sources_sha256": {"selection_manifest": digest(MAP1), "sample_selection": digest(MAP2)},
        "label_index_sha256": digest(INDEX),
        "labels_opened_only_after_prediction_seal": True})
    print(json.dumps({"status": report["status"], "aggregate_match": metric_match,
                      "cases": len(records)}, sort_keys=True))
    if not metric_match:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
