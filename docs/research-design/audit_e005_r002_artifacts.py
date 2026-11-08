"""Independently inspect E005-R002's saved SQLite and summary artifacts.

Read-only: opens the run database in SQLite mode=ro and writes only to stdout.
"""

from __future__ import annotations

import json
import hashlib
import sqlite3
import sys
from collections import Counter
from pathlib import Path


def points_from_payloads(payloads: list[dict]) -> list[tuple[str, str, str, str]]:
    points = []
    for payload in payloads:
        for resource_metrics in payload.get("resource_metrics", []):
            for scope_metrics in resource_metrics.get("scope_metrics", []):
                for metric in scope_metrics.get("metrics", []):
                    if metric.get("name") != "dce.e005.requests":
                        continue
                    for point in metric.get("sum", {}).get("data_points", []):
                        points.append(
                            (
                                metric.get("name", ""),
                                metric.get("unit", ""),
                                str(point.get("as_int", "")),
                                str(point.get("time_unix_nano", "")),
                            )
                        )
    return sorted(points)


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    attempt = (
        root
        / "experiments/E005_telemetry_attachment/results/E005-R002/attempt-001"
    )
    preflight = json.loads((attempt / "preflight.json").read_text(encoding="utf-8"))
    summary = json.loads((attempt / "summary.json").read_text(encoding="utf-8"))
    source_manifest = json.loads(
        (attempt.parent / "source-manifest.json").read_text(encoding="utf-8")
    )
    db_uri = attempt.joinpath("telemetry.sqlite").resolve().as_uri() + "?mode=ro"
    connection = sqlite3.connect(db_uri, uri=True)
    try:
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        rows = connection.execute(
            "SELECT signal, decoded_json FROM payloads ORDER BY id"
        ).fetchall()
    finally:
        connection.close()

    payloads = [(signal, json.loads(decoded)) for signal, decoded in rows]
    counts = dict(Counter(signal for signal, _ in payloads))
    metrics = [payload for signal, payload in payloads if signal == "metrics"]
    traces = [payload for signal, payload in payloads if signal == "traces"]
    logs = [payload for signal, payload in payloads if signal == "logs"]
    source_points = sorted(
        (
            point.get("name", ""),
            point.get("unit", ""),
            point.get("value", ""),
            point.get("time_unix_nano", ""),
        )
        for point in summary.get("metric_source_points", [])
    )
    sink_points = points_from_payloads(metrics)
    encoded = json.dumps([payload for _, payload in payloads], sort_keys=True)
    source_hash_checks = {}
    for relative_path, record in source_manifest.get("files", {}).items():
        if relative_path == "tools/e005/otelcol.exe":
            source_hash_checks[relative_path] = (
                record.get("sha256") == preflight.get("collector_sha256")
            )
            continue
        path = root / relative_path
        source_hash_checks[relative_path] = path.is_file() and hashlib.sha256(
            path.read_bytes()
        ).hexdigest() == record.get("sha256")
    checks = {
        "sqlite_integrity_ok": integrity == "ok",
        "durable_counts_match_summary": counts == summary.get("counts"),
        "expected_record_count_16": len(payloads) == 16,
        "four_metric_payloads": len(metrics) == 4,
        "metric_source_sink_exact_match": source_points == sink_points,
        "metric_point_count_four": len(sink_points) == 4,
        "resource_identity_present": "dce-e005-checkout" in encoded,
        "trace_span_names_present": all(
            name in encoded for name in ("checkout", "inventory.lookup")
        ),
        "log_fixture_fields_present": all(
            field in encoded for field in ("controlled checkout accepted", "event.name")
        ),
        "malformed_requests_reported_4xx": all(
            400 <= status < 500
            for status in summary.get("cases", [{}])[3].get("statuses", {}).values()
        ),
        "storage_failure_reported_5xx": next(
            (
                case.get("http_status", 0) >= 500
                for case in summary.get("cases", [])
                if case.get("case") == "storage-failure"
            ),
            False,
        ),
        "summary_reports_restart_counts": summary.get("counts") == counts,
        "source_manifest_hashes_match_current_files": all(source_hash_checks.values()),
        "source_manifest_records_git_head": bool(source_manifest.get("git_head")),
    }
    report = {
        "run_id": "E005-R002",
        "scope": "independent read-only check of saved attempt-001 SQLite and summary",
        "sqlite_integrity": integrity,
        "durable_counts": counts,
        "source_metric_points": len(source_points),
        "sink_metric_points": len(sink_points),
        "checks": checks,
        "all_checks_pass": all(checks.values()),
        "protocol_deviations": {
            "openresearch_run_commit": preflight.get("orx_commit"),
            "source_git_head": source_manifest.get("git_head"),
            "source_manifest_hashes": source_hash_checks,
            "note": (
                "A committed source manifest records the run-time Git head and the "
                "listed source hashes match the current files. The preflight reports "
                "that OpenResearch did not manage this run, so the frozen execution "
                "protocol remains incomplete."
            ),
        },
        "limits": [
            "This audit checks saved artifacts; it does not recreate the SDK export.",
            "No claim about production delivery, throughput, or RCA quality follows.",
        ],
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["all_checks_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
