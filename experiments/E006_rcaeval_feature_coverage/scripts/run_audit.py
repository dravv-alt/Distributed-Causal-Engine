"""Label-blind aggregation of the frozen RCAEval case field audits for E006."""
from __future__ import annotations

import hashlib
import json
import os
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments" / "E006_rcaeval_feature_coverage"
RUN = EXP / "results" / "E006-R001"
CONFIG = json.loads((EXP / "configuration.json").read_text(encoding="utf-8"))
EXPECTED = set(CONFIG["blind_case_ids"])


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_new(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def main() -> None:
    RUN.mkdir(parents=True, exist_ok=False)
    git_head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                              text=True, capture_output=True).stdout.strip() or "UNKNOWN"
    git_status = subprocess.run(["git", "status", "--short"], cwd=ROOT,
                                text=True, capture_output=True).stdout.splitlines()
    source_files = [EXP / "configuration.json", EXP / "protocol.md", Path(__file__)]
    input_paths = {case: ROOT / "data" / "rcaeval" / "inference" / case / "field-audit.json"
                   for case in sorted(EXPECTED)}
    missing = [str(path.relative_to(ROOT)) for path in input_paths.values() if not path.is_file()]
    if missing:
        write_new(RUN / "failure.json", {"status": "FAIL", "missing_inputs": missing})
        raise FileNotFoundError(missing)

    audits = {}
    for case, path in input_paths.items():
        audit = json.loads(path.read_text(encoding="utf-8"))
        if audit.get("blind_case_id") != case:
            raise ValueError(f"blind case identity mismatch in {path}")
        if audit.get("dataset_revision") != CONFIG["revision"]:
            raise ValueError(f"dataset revision mismatch in {path}")
        if audit.get("labels_loaded_into_audit") is not False:
            raise ValueError(f"input is not certified label-blind: {path}")
        metrics = audit.get("metrics")
        if not isinstance(metrics, dict) or not isinstance(metrics.get("field_catalog"), list):
            raise ValueError(f"metric field catalog missing: {path}")
        audits[case] = audit

    features_by_case: dict[str, set[str]] = {}
    case_results = {}
    for case in sorted(audits):
        audit = audits[case]
        metrics = audit["metrics"]
        fields = metrics["field_catalog"]
        names = [field["name"] for field in fields]
        if len(names) != len(set(names)) or "time" not in names:
            raise ValueError(f"duplicate columns or missing time column: {case}")
        features = set(names) - {"time"}
        features_by_case[case] = features
        expected_feature_count = metrics.get("feature_columns")
        if expected_feature_count is not None and expected_feature_count != len(features):
            raise ValueError(f"feature count mismatch in {case}")
        cross = audit.get("cross_modality", {})
        case_results[case] = {
            "metric_rows": metrics.get("rows"),
            "metric_timestamp_distinct": metrics.get("timestamp", {}).get("distinct"),
            "metric_columns_including_time": len(names),
            "metric_feature_count_excluding_time": len(features),
            "fields": fields,
            "missing_cells": sum(int(field.get("null_count", 0)) for field in fields),
            "logs": {"available": audit.get("logs", {}).get("available", False),
                     "rows": audit.get("logs", {}).get("rows")},
            "traces": {"available": audit.get("traces", {}).get("available", False),
                       "rows": audit.get("traces", {}).get("rows")},
            "metric_log_timestamp_overlap": cross,
        }

    union = set.union(*features_by_case.values())
    intersection = set.intersection(*features_by_case.values())
    input_hashes = {str(path.relative_to(ROOT)): sha256(path) for path in input_paths.values()}
    result = {
        "experiment_id": "E006",
        "run_id": "E006-R001",
        "status": "COMPLETED_DESCRIPTIVE_AUDIT",
        "dataset_revision": CONFIG["revision"],
        "blind_cases": sorted(EXPECTED),
        "case_count": len(audits),
        "feature_union_count": len(union),
        "feature_intersection_count": len(intersection),
        "feature_union": sorted(union),
        "feature_intersection": sorted(intersection),
        "case_results": case_results,
        "interpretation": [
            "Nine preselected cases are not a random sample or complete dataset coverage.",
            "Metric semantics, units, temporality, aggregation and reset behavior remain UNKNOWN.",
            "Exact integer metric/log timestamp overlap does not prove common units or aligned windows.",
            "This is a descriptive input-coverage audit, not DCE feature-extractor or RCA evaluation."
        ]
    }
    write_new(RUN / "feature-coverage.json", result)
    manifest = {
        "execution_mode": "standalone local process; offline input audit; OpenResearch not used",
        "command": "python experiments/E006_rcaeval_feature_coverage/scripts/run_audit.py",
        "python": sys.version,
        "platform": platform.platform(),
        "orx_available_on_path": os.path.exists(os.path.join(os.path.dirname(sys.executable), "orx.exe")),
        "git_head": git_head,
        "git_status_excerpt": git_status[:100],
        "configuration_sha256": sha256(EXP / "configuration.json"),
        "protocol_sha256": sha256(EXP / "protocol.md"),
        "runner_sha256": sha256(Path(__file__)),
        "input_audit_sha256": input_hashes,
        "output_sha256": sha256(RUN / "feature-coverage.json"),
        "network_access": "none by runner; local files only"
    }
    write_new(RUN / "source-manifest.json", manifest)
    print(json.dumps({"status": result["status"], "cases": len(audits),
                      "feature_union": len(union), "feature_intersection": len(intersection),
                      "output": str(RUN / "feature-coverage.json")}, sort_keys=True))


if __name__ == "__main__":
    main()
