"""Open evaluator labels only after predictions are sealed and audited."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "E009_rcaeval_topology_baseline"
RUN = EXP / "results" / "E009-R001"
CONFIG = json.loads((EXP / "configuration.json").read_text(encoding="utf-8"))
INDEX = ROOT / "data" / "rcaeval" / "evaluator-only" / "index-afeacb1" / "cases.parquet"
SELECTION = ROOT / "data" / "rcaeval" / "evaluator-only" / "sample-selection-2026-11-07.json"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def emit(path: Path, payload: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")


def topk_credit(ranked: list[dict], target: str, k: int) -> float:
    if not any(row["service"] == target for row in ranked):
        return 0.0
    target_score = next(row["score"] for row in ranked if row["service"] == target)
    higher = sum(row["score"] > target_score for row in ranked)
    tied = sum(row["score"] == target_score for row in ranked)
    return max(0.0, min(1.0, (k - higher) / tied))


def evaluate() -> dict:
    seal_path = RUN / "prediction-seal.json"
    audit_path = RUN / "independent-audit.json"
    pred_path = RUN / "predictions.jsonl"
    seal = json.loads(seal_path.read_text(encoding="utf-8"))
    if digest(pred_path) != seal["prediction_sha256"]:
        raise ValueError("prediction file changed after sealing")
    if json.loads(audit_path.read_text(encoding="utf-8")).get("all_cases_match") is not True:
        raise ValueError("independent label-blind audit did not pass")

    # Evaluator-only sources are intentionally opened only after the seal checks above.
    selection = json.loads(SELECTION.read_text(encoding="utf-8"))
    if selection.get("dataset_revision") != CONFIG["revision"]:
        raise ValueError("evaluator selection revision mismatch")
    case_map = {row["blind_case_id"]: row["source_case_name"] for row in selection["samples"]}
    if set(case_map) != set(CONFIG["blind_case_ids"]):
        raise ValueError("selection mapping does not cover exactly the frozen blind cases")
    labels_frame = pl.read_parquet(INDEX, columns=["case", "root_cause_service"])
    source_names = list(case_map.values())
    selected = labels_frame.filter(pl.col("case").is_in(source_names))
    rows = selected.to_dicts()
    labels = {row["case"]: row["root_cause_service"] for row in rows}
    if len(rows) != len(source_names) or len(labels) != len(source_names):
        raise ValueError("evaluator join is missing or ambiguous for selected cases")

    predictions = [json.loads(line) for line in pred_path.read_text(encoding="utf-8").splitlines()]
    by_method = {method: {"top1_tie_aware_sum": 0.0, "top3_tie_aware_sum": 0.0,
                          "top1_deterministic_hits": 0, "top3_deterministic_hits": 0,
                          "root_set_exact_hits": 0, "abstentions": 0,
                          "root_candidate_hits": 0, "root_explanation_hits": 0}
                 for method in CONFIG["methods"]}
    case_metrics = []
    for prediction in predictions:
        blind_id = prediction["blind_case_id"]
        target = labels[case_map[blind_id]]
        candidate_names = {item["service"] for item in prediction["methods"]["topology_shared_callers_v1"]}
        per_method = {}
        for method in CONFIG["methods"]:
            ranked = prediction["methods"][method]
            scores = by_method[method]
            present = target in {item["service"] for item in ranked}
            top1 = topk_credit(ranked, target, 1)
            top3 = topk_credit(ranked, target, 3)
            deterministic_rank = next((i for i, item in enumerate(ranked, start=1)
                                       if item["service"] == target), None)
            top_candidates = set()
            if ranked:
                maximum = max(item["score"] for item in ranked)
                top_candidates = {item["service"] for item in ranked if item["score"] == maximum}
            exact_set = top_candidates == {target}
            scores["top1_tie_aware_sum"] += top1
            scores["top3_tie_aware_sum"] += top3
            scores["top1_deterministic_hits"] += int(deterministic_rank == 1)
            scores["top3_deterministic_hits"] += int(deterministic_rank is not None and deterministic_rank <= 3)
            scores["root_set_exact_hits"] += int(exact_set)
            scores["abstentions"] += int(not ranked)
            scores["root_candidate_hits"] += int(present)
            topology_row = next((item for item in ranked if item["service"] == target), None)
            scores["root_explanation_hits"] += int(
                method == "topology_shared_callers_v1" and topology_row is not None
                and bool(topology_row["reachable_callers"]))
            per_method[method] = {"top1_tie_aware": top1, "top3_tie_aware": top3,
                                  "top1_deterministic": int(deterministic_rank == 1),
                                  "top3_deterministic": int(deterministic_rank is not None and deterministic_rank <= 3),
                                  "root_set_exact": int(exact_set), "root_candidate_present": present,
                                  "root_explanation_present": bool(topology_row and topology_row["reachable_callers"])
                                  if method == "topology_shared_callers_v1" else False}
        case_metrics.append({"blind_case_id": blind_id, "candidate_count": prediction["candidate_count"],
                             "trace_available": prediction["trace_available"],
                             "topology_abstained": not prediction["methods"]["topology_shared_callers_v1"],
                             "root_candidate_present": target in candidate_names,
                             "method_metrics": per_method})

    n = len(predictions)
    aggregate = {}
    for method, totals in by_method.items():
        aggregate[method] = {
            "cases": n,
            "top1_tie_aware": totals["top1_tie_aware_sum"] / n,
            "top3_tie_aware": totals["top3_tie_aware_sum"] / n,
            "top1_deterministic": totals["top1_deterministic_hits"] / n,
            "top3_deterministic": totals["top3_deterministic_hits"] / n,
            "root_set_exact_accuracy": totals["root_set_exact_hits"] / n,
            "abstentions": totals["abstentions"],
            "root_candidate_coverage": totals["root_candidate_hits"] / n,
            "root_explanation_coverage": totals["root_explanation_hits"] / n,
        }
    differences = {
        metric: aggregate["topology_shared_callers_v1"][metric] - aggregate["graph_disabled_uniform_v1"][metric]
        for metric in ("top1_tie_aware", "top3_tie_aware", "top1_deterministic", "top3_deterministic")
    }
    return {
        "experiment_id": "E009", "run_id": "E009-R001", "dataset_revision": CONFIG["revision"],
        "case_count": n, "aggregate": aggregate, "topology_minus_uniform": differences,
        "per_blind_case": case_metrics,
        "evaluator_artifacts": {"selection_sha256": digest(SELECTION), "label_index_sha256": digest(INDEX)},
        "label_strings_written_to_report": False,
        "limits": ["Nine cases are a deliberately selected small sample, not a probability sample.",
                   "No confidence interval or significance claim is reported.",
                   "Trace-only topology can abstain and cannot establish a faulty symptom.",
                   "Exact service-name matching may count naming mismatches as absent candidates.",
                   "This run is retrospective sample evaluation, not online detection or causal inference."]
    }


def main() -> None:
    result = evaluate()
    emit(RUN / "evaluation.json", result)
    print(json.dumps({"cases": result["case_count"], "aggregate": result["aggregate"],
                      "topology_minus_uniform": result["topology_minus_uniform"],
                      "output": str(RUN / "evaluation.json")}, sort_keys=True))


if __name__ == "__main__":
    main()
