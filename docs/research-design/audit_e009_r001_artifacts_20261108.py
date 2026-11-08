"""Read-only audit of E009-R001's sealed predictions and final artifact manifest."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT / "experiments/E009_rcaeval_topology_baseline"
RUN = EXP / "results/E009-R001"
OUT = RUN / "independent-artifact-audit-addendum-2026-11-08.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> None:
    final_manifest_path = RUN / "artifact-manifest-final.json"
    final_manifest = load_json(final_manifest_path)
    manifest_failures = []
    for relative, expected in final_manifest["files"].items():
        path = RUN / relative
        if not path.is_file():
            manifest_failures.append({"path": relative, "problem": "missing"})
        elif path.stat().st_size != expected["bytes"] or sha256(path) != expected["sha256"]:
            manifest_failures.append({"path": relative, "problem": "size_or_hash_mismatch"})

    preflight = load_json(RUN / "preflight.json")
    seal = load_json(RUN / "prediction-seal.json")
    predictions_path = RUN / "predictions.jsonl"
    prediction_lines = predictions_path.read_text(encoding="utf-8").splitlines()
    blind_audit = load_json(RUN / "independent-audit.json")
    evaluation = load_json(RUN / "evaluation.json")
    eval_audit = load_json(RUN / "independent-evaluation-audit-retry.json")
    eval_attempt = load_json(RUN / "evaluation-attempt-002.json")
    failed_attempt = load_json(RUN / "evaluation-attempt-001-failure.json")

    input_hash_failures = []
    for relative, expected in preflight["model_input_hashes"].items():
        path = ROOT / relative
        if not path.is_file() or sha256(path) != expected:
            input_hash_failures.append(relative)

    checks = {
        "final_manifest_all_23_artifacts_match": (
            len(final_manifest["files"]) == 23 and not manifest_failures
        ),
        "all_sealed_prediction_rows_match": (
            len(prediction_lines) == seal["prediction_rows"] == 9
            and sha256(predictions_path) == seal["prediction_sha256"]
            == preflight["prediction_sha256"]
        ),
        "label_blind_audit_passed_for_all_cases": (
            blind_audit["all_cases_match"]
            and not blind_audit["labels_opened"]
            and blind_audit["prediction_sha256"] == seal["prediction_sha256"]
        ),
        "evaluator_retry_followed_seal_and_blind_audit": (
            eval_attempt["outcome"] == "COMPLETED"
            and eval_attempt["label_opened_after_prediction_seal_and_independent_audit"]
            and eval_attempt["prediction_sha256"] == seal["prediction_sha256"]
        ),
        "independent_evaluator_recomputed_nine_cases": (
            eval_audit["status"] == "PASS"
            and eval_audit["case_join_count"] == eval_audit["case_result_count"] == 9
            and eval_audit["prediction_sha256"] == seal["prediction_sha256"]
        ),
        "evaluation_keeps_all_nine_cases": evaluation["case_count"] == 9,
        "local_trace_input_hashes_still_match": not input_hash_failures,
        "failed_attempts_are_preserved": (
            failed_attempt["outcome"] == "FAILED"
            and (RUN / "independent-evaluation-audit.json").is_file()
            and load_json(RUN / "independent-evaluation-audit.json")["status"] == "FAIL"
        ),
    }
    payload = {
        "audit": "E009-R001 final artifact manifest, sealed inference, and evaluation chain",
        "audit_date": "2026-11-08",
        "scope": "Read-only verification of preserved local artifacts; no inference rerun",
        "manifest_entries": len(final_manifest["files"]),
        "manifest_failures": manifest_failures,
        "trace_input_hash_failures": input_hash_failures,
        "prediction_sha256": seal["prediction_sha256"],
        "evaluation_aggregate": evaluation["aggregate"],
        "topology_minus_uniform": evaluation["topology_minus_uniform"],
        "verifier": Path(__file__).relative_to(ROOT).as_posix(),
        "verifier_sha256": sha256(Path(__file__)),
        "checks": checks,
        "passed": sum(value is True for value in checks.values()),
        "total": len(checks),
        "interpretation_limit": (
            "This verifies the selected nine-case artifact chain only. It does not support "
            "population inference, online detection, causal claims, or a full-campaign pass."
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
