"""Score sealed E010 predictions only after independent blind audit."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import polars as pl

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "E010_rcaeval_topology_temporal"
RUN = EXP / "results" / "E010-R001"
CFG = json.loads((EXP / "configuration.json").read_text(encoding="utf-8"))
EVAL = ROOT / "data" / "rcaeval" / "evaluator-only"
MAP_ONE = EVAL / "selection-manifest.json"
MAP_EIGHT = EVAL / "sample-selection-2026-11-07.json"
INDEX = EVAL / "index-afeacb1" / "cases.parquet"
METHODS = ["topology_only_e009", "graph_disabled_uniform_e009"] + [
    method for bound in ("0.01", "0.05", "0.10")
    for method in (f"temporal_only_{bound}", f"topology_temporal_{bound}")]


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_new(path: Path, obj: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")


def credits(ranked: list[dict], target: str, k: int) -> float:
    match = next((r["score"] for r in ranked if r["service"] == target), None)
    if match is None:
        return 0.0
    higher = sum(r["score"] > match for r in ranked)
    tied = sum(r["score"] == match for r in ranked)
    return max(0.0, min(1.0, (k - higher) / tied))


def load_mapping() -> tuple[dict[str, str], dict[str, str]]:
    first, rest = json.loads(MAP_ONE.read_text(encoding="utf-8")), json.loads(MAP_EIGHT.read_text(encoding="utf-8"))
    if first.get("dataset_revision") != CFG["revision"] or rest.get("dataset_revision") != CFG["revision"]:
        raise ValueError("selection revision mismatch")
    if first.get("root_cause_fault_injection_fields_read_for_selection") is not False:
        raise ValueError("single-case selection does not establish label-blind selection")
    if rest.get("root_cause_fault_injection_fields_read_for_selection") is not False:
        raise ValueError("group selection does not establish label-blind selection")
    mapping = {first["selected_case_blind_id"]: first["selected_case_name"]}
    groups = {first["selected_case_blind_id"]: "RE2-TT"}
    mapping.update({r["blind_case_id"]: r["source_case_name"] for r in rest["samples"]})
    groups.update({r["blind_case_id"]: r["dataset_group"] for r in rest["samples"]})
    if set(mapping) != set(CFG["blind_case_ids"]) or len(set(mapping.values())) != len(mapping):
        raise ValueError("exact label mapping does not match frozen sample")
    return mapping, groups


def main() -> None:
    seal = json.loads((RUN / "prediction-seal.json").read_text(encoding="utf-8"))
    pred_path = RUN / "predictions.jsonl"
    if sha(pred_path) != seal["prediction_sha256"]:
        raise ValueError("prediction file changed after seal")
    if json.loads((RUN / "independent-audit.json").read_text(encoding="utf-8")).get("status") != "PASS":
        raise ValueError("independent label-blind audit must pass before labels open")

    # Evaluator-only files are opened after the prediction seal/audit checks.
    mapping, groups = load_mapping()
    label_rows = pl.read_parquet(INDEX, columns=["case", "root_cause_service"]).filter(
        pl.col("case").is_in(list(mapping.values()))).to_dicts()
    targets = {row["case"]: row["root_cause_service"] for row in label_rows}
    if len(label_rows) != len(mapping) or len(targets) != len(mapping):
        raise ValueError("evaluator exact join missing or ambiguous")

    predictions = [json.loads(line) for line in pred_path.read_text(encoding="utf-8").splitlines()]
    if len(predictions) != len(CFG["blind_case_ids"]):
        raise ValueError("wrong number of predictions")
    accum = {m: {"top1_tie": 0.0, "top3_tie": 0.0, "top1_det": 0,
                 "top3_det": 0, "topset": 0, "abstain": 0,
                 "candidate": 0} for m in METHODS}
    per_case = []
    for pred in predictions:
        cid = pred["blind_case_id"]
        target = targets[mapping[cid]]
        per_method = {}
        for method in METHODS:
            ranked = pred["methods"][method]
            present = any(row["service"] == target for row in ranked)
            rank_pos = next((i for i, row in enumerate(ranked, 1) if row["service"] == target), None)
            score = next((row["score"] for row in ranked if row["service"] == target), None)
            best = max((row["score"] for row in ranked), default=None)
            top_set = {row["service"] for row in ranked if row["score"] == best} if best is not None else set()
            a = accum[method]
            t1, t3 = credits(ranked, target, 1), credits(ranked, target, 3)
            a["top1_tie"] += t1
            a["top3_tie"] += t3
            a["top1_det"] += int(rank_pos == 1)
            a["top3_det"] += int(rank_pos is not None and rank_pos <= 3)
            a["topset"] += int(top_set == {target})
            a["abstain"] += int(not ranked)
            a["candidate"] += int(present)
            per_method[method] = {
                "top1_tie_aware": t1, "top3_tie_aware": t3,
                "top1_deterministic": int(rank_pos == 1),
                "top3_deterministic": int(rank_pos is not None and rank_pos <= 3),
                "top_score_set_exact": int(top_set == {target}),
                "root_candidate_present": present,
                "root_score": score}
        per_case.append({"blind_case_id": cid, "dataset_group": groups[cid],
                         "trace_available": pred["trace_available"],
                         "candidate_count": pred["candidate_count"],
                         "abstained": pred["abstained"], "method_metrics": per_method,
                         "temporal_consistency": pred["temporal"]["temporal_consistency"],
                         "temporal_order_invariant": pred["row_order_exact"]})

    n = len(predictions)
    aggregate = {}
    for method, a in accum.items():
        aggregate[method] = {
            "cases": n, "top1_tie_aware": a["top1_tie"] / n,
            "top3_tie_aware": a["top3_tie"] / n,
            "top1_deterministic": a["top1_det"] / n,
            "top3_deterministic": a["top3_det"] / n,
            "top_score_set_exact_accuracy": a["topset"] / n,
            "abstentions": a["abstain"],
            "root_candidate_coverage": a["candidate"] / n}
    deltas = {}
    for method in METHODS:
        if method in ("topology_only_e009", "graph_disabled_uniform_e009"):
            continue
        deltas[method] = {metric: aggregate[method][metric] - aggregate["topology_only_e009"][metric]
                          for metric in ("top1_tie_aware", "top3_tie_aware",
                                         "top1_deterministic", "top3_deterministic")}
    temporal_consistency = {}
    for bound in ("0.01", "0.05", "0.10"):
        numer = denom = 0
        for pred in predictions:
            info = pred["temporal"]
            nrefs = info.get("parent_resolution_counts", {}).get("resolved_cross_service_parent", 0)
            frac = info.get("temporal_consistency", {}).get(bound)
            if nrefs and frac is not None:
                numer += frac * nrefs
                denom += nrefs
        temporal_consistency[bound] = {"weighted_supported_reference_fraction": numer / denom if denom else None,
                                       "resolved_cross_service_reference_count": denom}

    report = {
        "experiment_id": "E010", "run_id": "E010-R001", "dataset_revision": CFG["revision"],
        "case_count": n, "aggregate": aggregate, "localization_delta_vs_topology": deltas,
        "temporal_consistency": temporal_consistency,
        "all_temporal_orders_invariant": all(p["row_order_exact"] for p in predictions),
        "per_blind_case": per_case,
        "evaluator_source_hashes": {"selection_manifest": sha(MAP_ONE),
                                    "sample_selection": sha(MAP_EIGHT), "label_index": sha(INDEX)},
        "root_service_strings_in_report": False,
        "limits": ["The nine cases are selected, not a probability sample.",
                   "Timestamp units, timezone, clock synchronization, fault onset, and delay semantics are UNKNOWN.",
                   "Relative bounds are sensitivity settings, not physical propagation latency limits.",
                   "Span frequency/order is instrumentation-dependent; no symptom detector is evaluated.",
                   "This retrospective sample is not held-out or online evaluation."]}
    write_new(RUN / "evaluation.json", report)
    write_new(RUN / "evaluation-attempt.json", {
        "outcome": "COMPLETED", "prediction_sha256": seal["prediction_sha256"],
        "label_evaluation_opened_after_seal_and_independent_audit": True,
        "evaluator_source_hashes": report["evaluator_source_hashes"]})
    print(json.dumps({"cases": n, "aggregate": aggregate,
                      "localization_delta_vs_topology": deltas,
                      "temporal_consistency": temporal_consistency}, sort_keys=True))


if __name__ == "__main__":
    main()
