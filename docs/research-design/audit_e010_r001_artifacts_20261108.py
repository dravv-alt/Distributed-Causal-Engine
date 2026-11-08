"""Read-only integrity audit for the E010-R001 saved prediction/evaluation chain."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/E010_rcaeval_topology_temporal"
RUN = EXP / "results/E010-R001"
E009 = ROOT / "experiments/E009_rcaeval_topology_baseline/results/E009-R001"
OUT = RUN / "independent-artifact-audit-addendum-2026-11-08.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> None:
    manifest = load(RUN / "artifact-manifest.json")
    failures = []
    for entry in manifest["files"]:
        path = RUN / entry["path"]
        if not path.is_file():
            failures.append({"path": entry["path"], "problem": "missing"})
        elif path.stat().st_size != entry["bytes"] or sha256(path) != entry["sha256"]:
            failures.append({"path": entry["path"], "problem": "size_or_hash_mismatch"})

    preflight = load(RUN / "preflight.json")
    seal = load(RUN / "prediction-seal.json")
    pred = RUN / "predictions.jsonl"
    lines = pred.read_text(encoding="utf-8").splitlines()
    blind_audit = load(RUN / "independent-audit.json")
    evaluator_audit = load(RUN / "independent-evaluation-audit.json")
    evaluation = load(RUN / "evaluation.json")
    e009_pred = E009 / "predictions.jsonl"
    input_hash_failures = []
    for relative, expected in preflight["trace_input_hashes"].items():
        if not (ROOT / relative).is_file() or sha256(ROOT / relative) != expected:
            input_hash_failures.append(relative)
    e009_hash = sha256(e009_pred) if e009_pred.is_file() else None

    checks = {
        "all_ten_manifest_entries_match": len(manifest["files"]) == 10 and not failures,
        "nine_predictions_match_seal_and_preflight": (
            len(lines) == seal["prediction_rows"] == preflight["prediction_rows"] == 9
            and sha256(pred) == seal["prediction_sha256"] == preflight["prediction_sha256"]
        ),
        "E009_baseline_hash_matches": (
            e009_hash == preflight["e009_baseline_prediction_sha256"] == blind_audit["e009_baseline_sha256"]
        ),
        "trace_input_hashes_match": not input_hash_failures,
        "label_blind_audit_passed_without_labels": (
            blind_audit["status"] == "PASS" and blind_audit["all_cases_match"]
            and not blind_audit["labels_opened"]
            and blind_audit["prediction_sha256"] == seal["prediction_sha256"]
        ),
        "independent_evaluator_audit_passed": (
            evaluator_audit["status"] == "PASS" and evaluator_audit["aggregate_match"]
            and evaluator_audit["case_join_count"] == 9
            and evaluator_audit["prediction_sha256"] == seal["prediction_sha256"]
        ),
        "all_nine_cases_retained": evaluation["case_count"] == 9,
        "saturated_temporal_feature_explicit": all(
            item["weighted_supported_reference_fraction"] == 1.0
            for item in evaluation["temporal_consistency"].values()
        ),
    }
    payload = {
        "audit": "E010-R001 manifest, sealed inference, baseline and evaluator chain",
        "audit_date": "2026-11-08",
        "scope": "Read-only saved-artifact verification; no inference rerun",
        "manifest_entries": len(manifest["files"]),
        "manifest_failures": failures,
        "trace_input_hash_failures": input_hash_failures,
        "prediction_sha256": seal["prediction_sha256"],
        "e009_baseline_sha256": e009_hash,
        "metrics": evaluation["aggregate"],
        "verifier": Path(__file__).relative_to(ROOT).as_posix(),
        "verifier_sha256": sha256(Path(__file__)),
        "checks": checks,
        "passed": sum(value is True for value in checks.values()),
        "total": len(checks),
        "interpretation_limit": (
            "This verifies the saved nine-case local run. The raw timestamp units are unknown; "
            "the saturated proxy does not establish temporal causality or RCA effectiveness."
        ),
    }
    with OUT.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"passed": payload["passed"], "total": payload["total"], "output": str(OUT)}))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
