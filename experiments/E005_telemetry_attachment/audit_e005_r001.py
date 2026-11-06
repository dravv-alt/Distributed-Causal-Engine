"""Independent read-only verifier for the frozen E005-R001 SQLite artifacts."""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ATTEMPT = Path(__file__).resolve().parent / "results" / "E005-R001" / "attempt-007"
DB = ATTEMPT / "telemetry.sqlite"
RUN_SUMMARY = ATTEMPT / "summary.json"


def check(ok: bool, name: str, failures: list[str]) -> None:
    if not ok:
        failures.append(name)


def main() -> int:
    failures: list[str] = []
    summary = json.loads(RUN_SUMMARY.read_text(encoding="utf-8"))
    with sqlite3.connect(DB) as cx:
        cx.execute("PRAGMA integrity_check")
        rows = cx.execute("SELECT signal,sha256,payload,decoded_json FROM payloads ORDER BY id").fetchall()
    items = [(s, h, raw, json.loads(decoded)) for s, h, raw, decoded in rows]
    counts = {signal: sum(s == signal for s, *_ in items) for signal in ("traces", "metrics", "logs")}
    check(summary.get("status") == "PASS", "runner summary status", failures)
    check(counts == {"traces": 8, "metrics": 4, "logs": 4}, f"signal counts {counts}", failures)
    check(len(items) == 16, f"payload record count {len(items)}", failures)
    check(all(__import__("hashlib").sha256(raw).hexdigest() == digest for _, digest, raw, _ in items),
          "payload hashes", failures)
    check(all("dce-e005-checkout" in json.dumps(doc) for _, _, _, doc in items),
          "resource identity across signals", failures)

    metric_points = []
    for signal, _, _, doc in items:
        if signal != "metrics":
            continue
        for resource in doc.get("resource_metrics", []):
            for scope in resource.get("scope_metrics", []):
                for metric in scope.get("metrics", []):
                    if metric.get("name") == "dce.e005.requests":
                        for point in metric.get("sum", {}).get("data_points", []):
                            metric_points.append((metric.get("unit"), point.get("as_int"), point.get("time_unix_nano")))
    check(len(metric_points) == 4, f"metric point count {len(metric_points)}", failures)
    check(all(unit == "1" and value == "7" and int(ts) > 0 for unit, value, ts in metric_points),
          f"metric fields {metric_points}", failures)

    spans = []
    logs = []
    for signal, _, _, doc in items:
        if signal == "traces":
            for resource in doc.get("resource_spans", []):
                for scope in resource.get("scope_spans", []):
                    spans.extend(scope.get("spans", []))
        if signal == "logs":
            for resource in doc.get("resource_logs", []):
                for scope in resource.get("scope_logs", []):
                    logs.extend(scope.get("log_records", []))
    span_names = {span.get("name") for span in spans}
    check(len(spans) == 8, f"span count {len(spans)}", failures)
    check(span_names == {"checkout", "inventory.lookup"}, f"span names {span_names}", failures)
    roots = [s for s in spans if s.get("name") == "checkout"]
    children = [s for s in spans if s.get("name") == "inventory.lookup"]
    check(len(roots) == 4 and len(children) == 4, "root/child span denominators", failures)
    if len(roots) == 4 and len(children) == 4:
        parent_ids = {s.get("span_id") for s in roots}
        root_traces = {s.get("trace_id") for s in roots}
        check(all(s.get("parent_span_id") in parent_ids and s.get("trace_id") in root_traces for s in children),
              "trace parent links", failures)
        check(all(s.get("parent_span_id") is None for s in roots), "root span markers", failures)
    check(len(logs) == 4, f"log count {len(logs)}", failures)
    check(all(log.get("body", {}).get("string_value") == "controlled checkout accepted"
              and log.get("severity_text") == "INFO"
              and int(log.get("time_unix_nano", "0")) == 1_800_000_000_040_000_000
              for log in logs), "log body/severity/timestamp", failures)
    malformed = next(c for c in summary["cases"] if c["case"] == "malformed")
    storage = next(c for c in summary["cases"] if c["case"] == "storage-failure")
    check(malformed.get("statuses") == {"traces": 400, "metrics": 400, "logs": 400},
          "malformed OTLP rejection", failures)
    check(malformed.get("counts_unchanged") is True, "malformed no-write control", failures)
    check(storage.get("http_status", 0) >= 500, "storage outage response", failures)
    check(summary.get("counts") == counts, "restart counts match", failures)
    unknowns = ["metric timestamp was present and retained, but the SDK pre-export timestamp was not captured for exact equality comparison"]
    audit_status = "FAIL" if failures else ("REVIEW_REQUIRED" if unknowns else "PASS")
    result = {"run_id": "E005-R001", "attempt": "007", "independent_audit": audit_status,
              "records": len(items), "counts": counts, "metric_points": len(metric_points),
              "spans": len(spans), "logs": len(logs), "checks_failed": failures, "unknowns": unknowns}
    (ATTEMPT / "independent-audit-002.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
