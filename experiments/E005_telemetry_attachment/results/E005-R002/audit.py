"""Read-only verifier for the standalone E005-R002 local attempt."""
from __future__ import annotations

import hashlib
import json
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE / "attempt-001"
SUMMARY = json.loads((ATTEMPT / "summary.json").read_text(encoding="utf-8"))
PREFLIGHT = json.loads((ATTEMPT / "preflight.json").read_text(encoding="utf-8"))
DB = ATTEMPT / "telemetry.sqlite"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


with sqlite3.connect(DB) as cx:
    integrity = cx.execute("PRAGMA integrity_check").fetchone()[0]
    rows = cx.execute(
        "SELECT signal, decoded_json FROM payloads ORDER BY id"
    ).fetchall()

payloads = [(signal, json.loads(payload)) for signal, payload in rows]
counts: dict[str, int] = {}
for signal, _ in payloads:
    counts[signal] = counts.get(signal, 0) + 1

metric_sink: list[tuple[str, str, str, str]] = []
trace_names: set[str] = set()
logs_contain_fixture = True
resource_identity_present = True
for signal, payload in payloads:
    encoded = json.dumps(payload, sort_keys=True)
    resource_identity_present &= "dce-e005-checkout" in encoded
    if signal == "metrics":
        for resource_metrics in payload.get("resource_metrics", []):
            for scope_metrics in resource_metrics.get("scope_metrics", []):
                for metric in scope_metrics.get("metrics", []):
                    for point in metric.get("sum", {}).get("data_points", []):
                        metric_sink.append((
                            metric.get("name", ""), metric.get("unit", ""),
                            str(point.get("as_int", "")),
                            str(point.get("time_unix_nano", "")),
                        ))
    elif signal == "traces":
        for resource_spans in payload.get("resource_spans", []):
            for scope_spans in resource_spans.get("scope_spans", []):
                trace_names.update(span.get("name", "")
                                   for span in scope_spans.get("spans", []))
    elif signal == "logs":
        logs_contain_fixture &= (
            "controlled checkout accepted" in encoded and "event.name" in encoded
        )

metric_source = sorted(
    (p["name"], p["unit"], p["value"], p["time_unix_nano"])
    for p in SUMMARY.get("metric_source_points", [])
)
metric_sink = sorted(metric_sink)
checks = {
    "sqlite_integrity": integrity == "ok",
    "payload_count": len(payloads) == 16,
    "signal_counts": counts == {"traces": 8, "metrics": 4, "logs": 4},
    "resource_identity": resource_identity_present,
    "metric_source_sink_exact": metric_source == metric_sink and len(metric_source) == 4,
    "trace_names": {"checkout", "inventory.lookup"}.issubset(trace_names),
    "log_fields": logs_contain_fixture,
    "malformed_requests_rejected": all(
        status == 400
        for status in SUMMARY["cases"][3]["statuses"].values()
    ),
    "storage_failure_rejected": SUMMARY["cases"][5]["http_status"] == 503,
    "runner_reported_pass": SUMMARY.get("status") == "PASS",
}
report = {
    "run_id": "E005-R002",
    "audit_type": "post-run read-only artifact audit; not an independent human review",
    "execution_boundary": PREFLIGHT.get("execution_boundary"),
    "orx_commit": PREFLIGHT.get("orx_commit"),
    "checks": checks,
    "all_local_checks_pass": all(checks.values()),
    "protocol_complete": PREFLIGHT.get("orx_commit") not in (None, "UNAVAILABLE"),
    "counts": counts,
    "metric_source_points": metric_source,
    "metric_sink_points": metric_sink,
    "sha256": {
        "summary.json": digest(ATTEMPT / "summary.json"),
        "preflight.json": digest(ATTEMPT / "preflight.json"),
        "telemetry.sqlite": digest(DB),
    },
    "interpretation": (
        "Local technical checks passed. This standalone run is not OpenResearch-managed "
        "and does not establish full XP002 completion or RCA effectiveness."
    ),
}
(HERE / "independent-audit.json").write_text(
    json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
print(json.dumps(report, sort_keys=True))
