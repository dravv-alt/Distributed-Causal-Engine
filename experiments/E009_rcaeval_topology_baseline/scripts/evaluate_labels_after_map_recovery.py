"""Evaluator retry using both frozen selection records after prediction sealing."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "E009_rcaeval_topology_baseline"
RUN = EXP / "results" / "E009-R001"
CONFIG = json.loads((EXP / "configuration.json").read_text(encoding="utf-8"))
EVAL_ROOT = ROOT / "data" / "rcaeval" / "evaluator-only"
INDEX = EVAL_ROOT / "index-afeacb1" / "cases.parquet"
INITIAL_SELECTION = EVAL_ROOT / "selection-manifest.json"
GROUP_SELECTION = EVAL_ROOT / "sample-selection-2026-11-07.json"


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


def topk_credit(ranked: list[dict], target: str, k: int) -> float:
    if not any(row["service"] == target for row in ranked):
        return 0.0
    target_score = next(row["score"] for row in ranked if row["service"] == target)
    higher = sum(row["score"] > target_score for row in ranked)
    tied = sum(row["score"] == target_score for row in ranked)
    return max(0.0, min(1.0, (k - higher) / tied))


def combine_mappings() -> tuple[dict[str, str], dict[str, str]]:
    first = json.loads(INITIAL_SELECTION.read_text(encoding="utf-8"))
    rest = json.loads(GROUP_SELECTION.read_text(encoding="utf-8"))
    if first.get("dataset_revision") != CONFIG["revision"] or rest.get("dataset_revision") != CONFIG["revision"]:
        raise ValueError("selection records do not match pinned dataset revision")
    if first.get("root_cause_fault_injection_fields_read_for_selection") is not False:
        raise ValueError("first selection record does not certify label-blind selection")
    if rest.get("root_cause_fault_injection_fields_read_for_selection") is not False:
        raise ValueError("group selection record does not certify label-blind selection")
    mapping = {first["selected_case_blind_id"]: first["selected_case_name"]}
    mapping.update({row["blind_case_id"]: row["source_case_name"] for row in rest["samples"]})
    groups = {first["selected_case_blind_id"]: "RE2-TT"}
    groups.update({row["blind_case_id"]: row["dataset_group"] for row in rest["samples"]})
    if set(mapping) != set(CONFIG["blind_case_ids"]):
        raise ValueError("combined evaluator selection records do not exactly cover the frozen cases")
    if len(set(mapping.values())) != len(mapping):
        raise ValueError("duplicate source case in combined selection records")
    return mapping, groups


def main() -> None:
    seal = json.loads((RUN / "prediction-seal.json").read_text(encoding="utf-8"))
    pred_path = RUN / "predictions.jsonl"
    if digest(pred_path) != seal["prediction_sha256"]:
        raise ValueError("prediction file changed after seal")
    audit = json.loads((RUN / "independent-audit.json").read_text(encoding="utf-8"))
    if audit.get("all_cases_match") is not True:
        raise ValueError("independent label-blind prediction audit did not pass")

    # This point is after prediction sealing and blind recomputation. Only now
    # are evaluator-only selection and label sources opened.
    case_map, case_groups = combine_mappings()
    frame = pl.read_parquet(INDEX, columns=["case", "root_cause_service"])
    rows = frame.filter(pl.col("case").is_in(list(case_map.values()))).to_dicts()
    labels = {row["case"]: row["root_cause_service"] for row in rows}
    if len(rows) != len(case_map) or len(labels) != len(case_map):
        raise ValueError("evaluator index join is missing or ambiguous")

    predictions = [json.loads(line) for line in pred_path.read_text(encoding="utf-8").splitlines()]
    if len(predictions) != len(CONFIG["blind_case_ids"]):
        raise ValueError("prediction count differs from frozen population")
    totals = {method: {"top1_tie": 0.0, "top3_tie": 0.0, "top1_hits": 0,
                       "top3_hits": 0, "top_set_hits": 0, "abstentions": 0,
                       "root_candidates": 0, "root_explanations": 0}
              for method in CONFIG["methods"]}
    case_results = []
    for prediction in predictions:
        blind_id = prediction["blind_case_id"]
        target = labels[case_map[blind_id]]
        topology_candidates = prediction["methods"]["topology_shared_callers_v1"]
        root_present = target in {row["service"] for row in topology_candidates}
        per_method = {}
        for method in CONFIG["methods"]:
            ranked = prediction["methods"][method]
            present = target in {row["service"] for row in ranked}
            t1, t3 = topk_credit(ranked, target, 1), topk_credit(ranked, target, 3)
            pos = next((i for i, row in enumerate(ranked, 1) if row["service"] == target), None)
            top_set = set()
            if ranked:
                max_score = max(row["score"] for row in ranked)
                top_set = {row["service"] for row in ranked if row["score"] == max_score}
            top_row = next((row for row in ranked if row["service"] == target), None)
            t = totals[method]
            t["top1_tie"] += t1
            t["top3_tie"] += t3
            t["top1_hits"] += int(pos == 1)
            t["top3_hits"] += int(pos is not None and pos <= 3)
            t["top_set_hits"] += int(top_set == {target})
            t["abstentions"] += int(not ranked)
            t["root_candidates"] += int(present)
            t["root_explanations"] += int(method == "topology_shared_callers_v1"
                                            and bool(top_row and top_row["reachable_callers"]))
            per_method[method] = {"top1_tie_aware": t1, "top3_tie_aware": t3,
                                  "top1_deterministic": int(pos == 1),
                                  "top3_deterministic": int(pos is not None and pos <= 3),
                                  "top_score_set_exact": int(top_set == {target}),
                                  "root_candidate_present": present,
                                  "root_explanation_present": bool(top_row and top_row["reachable_callers"])
                                  if method == "topology_shared_callers_v1" else False}
        case_results.append({"blind_case_id": blind_id, "dataset_group": case_groups[blind_id],
                             "trace_available": prediction["trace_available"],
                             "candidate_count": prediction["candidate_count"],
                             "root_candidate_present": root_present,
                             "topology_abstained": not topology_candidates,
                             "method_metrics": per_method})

    n = len(predictions)
    aggregate = {}
    for method, t in totals.items():
        aggregate[method] = {"cases": n, "top1_tie_aware": t["top1_tie"] / n,
                             "top3_tie_aware": t["top3_tie"] / n,
                             "top1_deterministic": t["top1_hits"] / n,
                             "top3_deterministic": t["top3_hits"] / n,
                             "top_score_set_exact_accuracy": t["top_set_hits"] / n,
                             "abstentions": t["abstentions"],
                             "root_candidate_coverage": t["root_candidates"] / n,
                             "root_explanation_coverage": t["root_explanations"] / n}
    deltas = {metric: aggregate["topology_shared_callers_v1"][metric]
              - aggregate["graph_disabled_uniform_v1"][metric]
              for metric in ("top1_tie_aware", "top3_tie_aware", "top1_deterministic", "top3_deterministic")}
    report = {"experiment_id": "E009", "run_id": "E009-R001", "evaluation_attempt": 2,
              "dataset_revision": CONFIG["revision"], "case_count": n,
              "aggregate": aggregate, "topology_minus_uniform": deltas,
              "per_blind_case": case_results,
              "selection_sources_sha256": {"first_case": digest(INITIAL_SELECTION),
                                           "remaining_cases": digest(GROUP_SELECTION)},
              "label_index_sha256": digest(INDEX), "label_strings_written_to_report": False,
              "label_access_order": "after prediction seal and independent blind audit",
              "limitations": ["Nine selected cases are not a probability sample.",
                              "No significance test or population confidence interval is reported.",
                              "Topology is structural evidence only, not a fault symptom or causal edge.",
                              "Exact service-name matching can treat naming differences as absent candidates.",
                              "This retrospective sample result does not establish online detection."]}
    write_new(RUN / "evaluation.json", report)
    write_new(RUN / "evaluation-attempt-002.json", {
        "attempt": 2, "outcome": "COMPLETED",
        "mapping_recovery": "Combined existing evaluator-only selection-manifest.json for RE2-TT-case-0001 with sample-selection-2026-11-07.json for blind cases 0002-0009.",
        "selection_sources_sha256": report["selection_sources_sha256"],
        "label_index_sha256": report["label_index_sha256"],
        "prediction_sha256": seal["prediction_sha256"],
        "label_opened_after_prediction_seal_and_independent_audit": True
    })
    print(json.dumps({"cases": n, "aggregate": aggregate,
                      "topology_minus_uniform": deltas,
                      "output": str(RUN / "evaluation.json")}, sort_keys=True))


if __name__ == "__main__":
    main()
