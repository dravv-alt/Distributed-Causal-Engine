"""Recompute E010 localization metrics independently after label separation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "E010_rcaeval_topology_temporal"
RUN = EXP / "results" / "E010-R001"
CFG = json.loads((EXP / "configuration.json").read_text(encoding="utf-8"))
EV = ROOT / "data" / "rcaeval" / "evaluator-only"
ONE = EV / "selection-manifest.json"
REST = EV / "sample-selection-2026-11-07.json"
INDEX = EV / "index-afeacb1" / "cases.parquet"
METHODS = ["topology_only_e009", "graph_disabled_uniform_e009"] + [
    method for bound in ("0.01", "0.05", "0.10")
    for method in (f"temporal_only_{bound}", f"topology_temporal_{bound}")]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def emit(path: Path, obj: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")


def tie_credit(entries: list[dict], label: str, k: int) -> float:
    scores = [x["score"] for x in entries if x["service"] == label]
    if not scores:
        return 0.0
    target = scores[0]
    ahead = len([x for x in entries if x["score"] > target])
    equal = len([x for x in entries if x["score"] == target])
    return max(0.0, min(1.0, (k - ahead) / equal))


def main() -> None:
    seal = json.loads((RUN / "prediction-seal.json").read_text(encoding="utf-8"))
    pred_path = RUN / "predictions.jsonl"
    if sha(pred_path) != seal["prediction_sha256"]:
        raise ValueError("prediction hash mismatch")
    if json.loads((RUN / "independent-audit.json").read_text(encoding="utf-8")).get("status") != "PASS":
        raise ValueError("label-blind audit must pass before evaluator source is opened")

    first = json.loads(ONE.read_text(encoding="utf-8"))
    rest = json.loads(REST.read_text(encoding="utf-8"))
    mapping = {first["selected_case_blind_id"]: first["selected_case_name"]}
    mapping.update({r["blind_case_id"]: r["source_case_name"] for r in rest["samples"]})
    if set(mapping) != set(CFG["blind_case_ids"]):
        raise ValueError("exact selection join does not cover frozen population")
    truth_rows = pl.read_parquet(INDEX, columns=["case", "root_cause_service"]).filter(
        pl.col("case").is_in(list(mapping.values()))).to_dicts()
    truth = {r["case"]: r["root_cause_service"] for r in truth_rows}
    if len(truth) != len(mapping) or len(truth_rows) != len(mapping):
        raise ValueError("independent exact evaluator join failed")

    predictions = [json.loads(line) for line in pred_path.read_text(encoding="utf-8").splitlines()]
    sums = {m: {"top1_tie": 0.0, "top3_tie": 0.0, "top1_det": 0,
                "top3_det": 0, "topset": 0, "abstain": 0, "candidate": 0}
            for m in METHODS}
    for pred in predictions:
        target = truth[mapping[pred["blind_case_id"]]]
        for method in METHODS:
            ranked = pred["methods"][method]
            pos = next((i for i, x in enumerate(ranked, 1) if x["service"] == target), None)
            best_score = max((x["score"] for x in ranked), default=None)
            best = {x["service"] for x in ranked if x["score"] == best_score} if best_score is not None else set()
            acc = sums[method]
            acc["top1_tie"] += tie_credit(ranked, target, 1)
            acc["top3_tie"] += tie_credit(ranked, target, 3)
            acc["top1_det"] += int(pos == 1)
            acc["top3_det"] += int(pos is not None and pos <= 3)
            acc["topset"] += int(best == {target})
            acc["abstain"] += int(len(ranked) == 0)
            acc["candidate"] += int(pos is not None)
    n = len(predictions)
    aggregate = {m: {"cases": n, "top1_tie_aware": a["top1_tie"] / n,
                     "top3_tie_aware": a["top3_tie"] / n,
                     "top1_deterministic": a["top1_det"] / n,
                     "top3_deterministic": a["top3_det"] / n,
                     "top_score_set_exact_accuracy": a["topset"] / n,
                     "abstentions": a["abstain"],
                     "root_candidate_coverage": a["candidate"] / n}
                  for m, a in sums.items()}
    saved = json.loads((RUN / "evaluation.json").read_text(encoding="utf-8"))
    aggregate_match = all(abs(aggregate[m][key] - saved["aggregate"][m][key]) < 1e-12
                          for m in METHODS for key in aggregate[m])
    delta_match = True
    for method in METHODS:
        if method in ("topology_only_e009", "graph_disabled_uniform_e009"):
            continue
        for key in ("top1_tie_aware", "top3_tie_aware", "top1_deterministic", "top3_deterministic"):
            expected = aggregate[method][key] - aggregate["topology_only_e009"][key]
            delta_match &= abs(expected - saved["localization_delta_vs_topology"][method][key]) < 1e-12
    report = {"status": "PASS" if aggregate_match and delta_match else "FAIL",
              "audit": "independent evaluator-side recomputation",
              "case_join_count": len(truth), "prediction_count": n,
              "aggregate_match": aggregate_match, "localization_deltas_match": delta_match,
              "prediction_sha256": seal["prediction_sha256"],
              "selection_hashes": {"one_case": sha(ONE), "remaining_cases": sha(REST)},
              "label_index_sha256": sha(INDEX), "label_strings_written": False}
    emit(RUN / "independent-evaluation-audit.json", report)
    print(json.dumps({"status": report["status"], "aggregate_match": aggregate_match,
                      "deltas_match": delta_match, "cases": n}, sort_keys=True))
    if report["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
