"""Read-only independent artifact audit for an ORX-managed E005-R002 attempt."""

from __future__ import annotations

import argparse
import json
import sqlite3
from collections import Counter
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("attempt_dir", type=Path)
    parser.add_argument("--expected-orx-commit", required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    attempt = args.attempt_dir.resolve()
    summary = json.loads((attempt / "summary.json").read_text(encoding="utf-8"))
    preflight = json.loads((attempt / "preflight.json").read_text(encoding="utf-8"))
    db_uri = (attempt / "telemetry.sqlite").resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(db_uri, uri=True)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        rows = connection.execute(
            "SELECT signal, decoded_json FROM payloads ORDER BY id"
        ).fetchall()
    finally:
        connection.close()

    records = [(signal, json.loads(payload)) for signal, payload in rows]
    counts = dict(Counter(signal for signal, _ in records))
    encoded = json.dumps([payload for _, payload in records], sort_keys=True)
    metrics = [payload for signal, payload in records if signal == "metrics"]
    sink_points = sorted(
        (
            metric.get("name", ""),
            metric.get("unit", ""),
            str(point.get("as_int", "")),
            str(point.get("time_unix_nano", "")),
        )
        for payload in metrics
        for resource_metrics in payload.get("resource_metrics", [])
        for scope_metrics in resource_metrics.get("scope_metrics", [])
        for metric in scope_metrics.get("metrics", [])
        if metric.get("name") == "dce.e005.requests"
        for point in metric.get("sum", {}).get("data_points", [])
    )
    source_points = sorted(
        (
            point.get("name", ""),
            point.get("unit", ""),
            point.get("value", ""),
            point.get("time_unix_nano", ""),
        )
        for point in summary.get("metric_source_points", [])
    )
    cases = {case.get("case"): case for case in summary.get("cases", [])}
    valid_cases = [cases.get(f"valid-{index}", {}) for index in range(1, 4)]
    malformed = cases.get("malformed", {})
    retry = cases.get("transient-rejection-retry", {})
    storage_failure = cases.get("storage-failure", {})
    checks = {
        "orx_commit_matches_expected": preflight.get("orx_commit")
        == args.expected_orx_commit,
        "local_synthetic_boundary_recorded": preflight.get("execution_boundary")
        == "loopback only; synthetic fixtures; no external requests",
        "sqlite_integrity_ok": integrity == "ok",
        "durable_record_count_and_signal_counts": len(records) == 16
        and counts == {"logs": 4, "metrics": 4, "traces": 8}
        and counts == summary.get("counts"),
        "all_valid_fixture_exports_succeeded": len(valid_cases) == 3
        and all(
            case.get("export_results")
            == {"traces": "SUCCESS", "metrics": "SUCCESS", "logs": "SUCCESS"}
            for case in valid_cases
        ),
        "malformed_requests_rejected_without_writes": malformed.get("statuses")
        == {"traces": 400, "metrics": 400, "logs": 400}
        and malformed.get("counts_unchanged") is True,
        "transient_rejection_recovered": retry.get("export_results")
        == {"traces": "SUCCESS", "metrics": "SUCCESS", "logs": "SUCCESS"},
        "storage_failure_not_acknowledged": storage_failure.get("http_status") == 503,
        "metric_source_sink_exact_match": len(source_points) == 4
        and source_points == sink_points,
        "resource_identity_present": "dce-e005-checkout" in encoded,
        "trace_fixture_names_present": all(
            name in encoded for name in ("checkout", "inventory.lookup")
        ),
        "log_fixture_fields_present": all(
            value in encoded
            for value in ("controlled checkout accepted", "event.name")
        ),
        "runner_reported_pass": summary.get("status") == "PASS",
    }
    report = {
        "run_id": "E005-R002",
        "orx_run_id": "c6653066-db74-4152-abf8-3e74efdc6147",
        "audit_type": "separate read-only recomputation from saved summary and SQLite",
        "sqlite_integrity": integrity,
        "durable_counts": counts,
        "source_metric_points": len(source_points),
        "sink_metric_points": len(sink_points),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "limits": [
            "Audit verifies saved local artifacts, not a new export execution.",
            "No throughput, production, RCA-quality, or causal claim follows.",
        ],
    }
    rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if report["all_checks_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
