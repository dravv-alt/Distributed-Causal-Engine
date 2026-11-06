"""Repeat E005's loopback ingestion protocol and capture metric timestamps before export."""
from __future__ import annotations

import json
import hashlib
import logging
import os
import platform
import socket
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

import requests
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LogRecord, LoggerProvider
from opentelemetry._logs import SeverityNumber
from opentelemetry.sdk._logs.export import SimpleLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
RUN = EXP / "results" / "E005-R002"
ATTEMPT = RUN / "attempt-001"
DB = ATTEMPT / "telemetry.sqlite"
RECEIVER = EXP / "receiver.py"
COLLECTOR = ROOT / "tools" / "e005" / "otelcol.exe"
if not COLLECTOR.exists():
    # OpenResearch runs an immutable Git snapshot without the large local binary.
    COLLECTOR = Path(r"C:\Users\bhavv\OneDrive\Desktop\Dravvya(4th Sem)\Projects\Distributed-Causal-Engine\tools\e005\otelcol.exe")
COLLECTOR_CONFIG = EXP / "collector.yaml"
RECEIVER_URL = "http://127.0.0.1:9000"
COLLECTOR_URL = "http://127.0.0.1:4318"
METRIC_SOURCE_POINTS: list[dict[str, str]] = []


class CaptureSpanExporter(OTLPSpanExporter):
    last_result = "NOT_CALLED"

    def export(self, spans):
        result = super().export(spans)
        self.last_result = getattr(result, "name", str(result))
        return result


class CaptureMetricExporter(OTLPMetricExporter):
    last_result = "NOT_CALLED"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_points: list[dict[str, str]] = []

    def export(self, metrics_data, timeout_millis=10_000, **kwargs):
        # Snapshot SDK data before the exporter serializes and sends it.
        for resource_metrics in metrics_data.resource_metrics:
            for scope_metrics in resource_metrics.scope_metrics:
                for metric in scope_metrics.metrics:
                    for point in getattr(metric.data, "data_points", []):
                        self.source_points.append({
                            "name": metric.name,
                            "unit": metric.unit,
                            "value": str(getattr(point, "value", "")),
                            "time_unix_nano": str(point.time_unix_nano),
                        })
        result = super().export(metrics_data, timeout_millis=timeout_millis, **kwargs)
        self.last_result = getattr(result, "name", str(result))
        return result


class CaptureLogExporter(OTLPLogExporter):
    last_result = "NOT_CALLED"

    def export(self, batch):
        result = super().export(batch)
        self.last_result = getattr(result, "name", str(result))
        return result


class FixtureIds:
    def __init__(self) -> None:
        self.trace = 0x1234567890ABCDEF1234567890ABCDEF
        self.span = 0x100

    def generate_trace_id(self) -> int:
        return self.trace

    def generate_span_id(self) -> int:
        self.span += 1
        return self.span


def wait_port(port: int, process: subprocess.Popen, log_path: Path) -> None:
    deadline = time.time() + 20
    while time.time() < deadline:
        if process.poll() is not None:
            raise RuntimeError(f"process exited {process.returncode}; see {log_path}")
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.25):
                return
        except OSError:
            time.sleep(0.2)
    raise TimeoutError(f"localhost:{port} did not start; see {log_path}")


def emit_signals(repetition: int) -> dict[str, str]:
    resource = Resource.create({
        "service.name": "dce-e005-checkout",
        "service.instance.id": f"e005-local-{repetition}",
        "deployment.environment.name": "e005-controlled",
    })
    endpoint = COLLECTOR_URL
    trace_ids = FixtureIds()
    tp = TracerProvider(resource=resource, id_generator=trace_ids)
    trace_exporter = CaptureSpanExporter(endpoint=f"{endpoint}/v1/traces", timeout=5)
    tp.add_span_processor(SimpleSpanProcessor(trace_exporter))
    tracer = tp.get_tracer("e005-fixture", "1.0")
    root_span = tracer.start_span("checkout", start_time=1_800_000_000_000_000_000,
                                  attributes={"fixture.repetition": repetition, "http.request.method": "POST"})
    with trace.use_span(root_span, end_on_exit=False):
        child = tracer.start_span("inventory.lookup", start_time=1_800_000_000_010_000_000,
                                  attributes={"fixture.item_count": 2})
        child.end(end_time=1_800_000_000_020_000_000)
    root_span.end(end_time=1_800_000_000_030_000_000)
    trace_result = trace_exporter.last_result
    tp.shutdown()

    metric_exporter = CaptureMetricExporter(endpoint=f"{endpoint}/v1/metrics", timeout=5)
    reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=60_000, export_timeout_millis=5_000)
    mp = MeterProvider(resource=resource, metric_readers=[reader])
    counter = mp.get_meter("e005-fixture", "1.0").create_counter("dce.e005.requests", unit="1")
    counter.add(7, {"route": "/checkout", "fixture.repetition": str(repetition)})
    # Shutdown performs the one final collection/export; calling force_flush as
    # well would intentionally export the cumulative counter twice.
    mp.shutdown()
    metric_result = metric_exporter.last_result
    METRIC_SOURCE_POINTS.extend(metric_exporter.source_points)

    lp = LoggerProvider(resource=resource)
    log_exporter = CaptureLogExporter(endpoint=f"{endpoint}/v1/logs", timeout=5)
    lp.add_log_record_processor(SimpleLogRecordProcessor(log_exporter))
    logger = lp.get_logger("e005-fixture", "1.0")
    logger.emit(LogRecord(timestamp=1_800_000_000_040_000_000,
                          observed_timestamp=1_800_000_000_040_000_000,
                          trace_id=trace_ids.trace,
                          span_id=0x102,
                          trace_flags=trace.TraceFlags(1),
                          severity_text="INFO", severity_number=SeverityNumber.INFO,
                          body="controlled checkout accepted",
                          resource=resource,
                          attributes={"fixture.repetition": repetition, "event.name": "checkout.accepted"}))
    log_result = log_exporter.last_result
    lp.shutdown()
    return {"traces": str(trace_result), "metrics": str(metric_result), "logs": str(log_result)}


def records() -> list[tuple[str, dict]]:
    with sqlite3.connect(DB) as cx:
        rows = cx.execute("SELECT signal,decoded_json FROM payloads ORDER BY id").fetchall()
    return [(signal, json.loads(payload)) for signal, payload in rows]


def counts() -> dict[str, int]:
    with sqlite3.connect(DB) as cx:
        return dict(cx.execute("SELECT signal,COUNT(*) FROM payloads GROUP BY signal").fetchall())


def expect(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)


def main() -> int:
    RUN.mkdir(parents=True, exist_ok=True)
    attempt = 2 if (RUN / "summary.json").exists() else 1
    while (RUN / f"attempt-{attempt:03d}").exists():
        attempt += 1
    attempt_dir = RUN / f"attempt-{attempt:03d}"
    attempt_dir.mkdir()
    global ATTEMPT, DB
    ATTEMPT = attempt_dir
    DB = ATTEMPT / "telemetry.sqlite"
    collector_log = (ATTEMPT / "collector.log").open("wb")
    receiver_log = (ATTEMPT / "receiver.log").open("wb")
    collector_version = subprocess.run([str(COLLECTOR), "--version"], capture_output=True, text=True, check=True).stdout.strip()
    with COLLECTOR.open("rb") as collector_file:
        collector_sha256 = hashlib.file_digest(collector_file, "sha256").hexdigest()
    preflight = {
        "run_id": "E005-R002",
        "orx_commit": os.environ.get("ORX_COMMIT", "UNAVAILABLE"),
        "python": sys.version,
        "platform": platform.platform(),
        "collector_version": collector_version,
        "collector_sha256": collector_sha256,
        "configuration_sha256": hashlib.sha256((EXP / "configuration-r002.json").read_bytes()).hexdigest(),
        "execution_boundary": "loopback only; synthetic fixtures; no external requests",
        "metric_timestamp_capture": "SDK metric data before serialization",
    }
    (ATTEMPT / "preflight.json").write_text(json.dumps(preflight, indent=2) + "\n", encoding="utf-8")
    env = os.environ.copy()
    env["E005_RECEIVER_PORT"] = "9000"
    env["E005_DB"] = str(DB)
    receiver = subprocess.Popen([sys.executable, str(RECEIVER)], cwd=ATTEMPT, env=env,
                                stdout=receiver_log, stderr=subprocess.STDOUT)
    collector = None
    outcomes: dict[str, object] = {"run_id": "E005-R002", "status": "RUNNING", "cases": []}
    try:
        wait_port(9000, receiver, RUN / "receiver.log")
        collector = subprocess.Popen([str(COLLECTOR), "--config", str(COLLECTOR_CONFIG)], cwd=ATTEMPT,
                                     stdout=collector_log, stderr=subprocess.STDOUT)
        wait_port(4318, collector, RUN / "collector.log")

        # Three deterministic fixture repetitions, using the real OTel SDK/exporters.
        for rep in range(1, 4):
            results = emit_signals(rep)
            outcomes["cases"].append({"case": f"valid-{rep}", "export_results": results})
            expect(all(v == "SUCCESS" for v in results.values()), f"valid export result {rep}: {results}")
        deadline = time.time() + 10
        while time.time() < deadline and any(counts().get(s, 0) < 3 for s in ("traces", "metrics", "logs")):
            time.sleep(0.1)
        valid_counts = counts()
        valid_expected = {"traces": 6, "metrics": 3, "logs": 3}
        expect(all(valid_counts.get(s, 0) == n for s, n in valid_expected.items()), f"valid counts {valid_counts}")

        # The collector must reject malformed OTLP protobuf bodies without reaching the sink.
        before = counts()
        malformed = {}
        for signal in ("traces", "metrics", "logs"):
            response = requests.post(f"{COLLECTOR_URL}/v1/{signal}", data=b"\x0a\xff",
                                     headers={"Content-Type": "application/x-protobuf"}, timeout=5)
            malformed[signal] = response.status_code
            expect(400 <= response.status_code < 500, f"malformed {signal} returned {response.status_code}")
        expect(counts() == before, "malformed request changed durable record counts")
        outcomes["cases"].append({"case": "malformed", "statuses": malformed, "counts_unchanged": True})

        # Force one pre-commit 503 at the DCE sink; collector retry must deliver it.
        requests.post(f"{RECEIVER_URL}/__control/fail-next-write", timeout=2).raise_for_status()
        retry_result = emit_signals(4)
        outcomes["cases"].append({"case": "transient-rejection-retry", "export_results": retry_result})
        expect(all(v == "SUCCESS" for v in retry_result.values()), f"retry exports failed: {retry_result}")
        deadline = time.time() + 10
        while time.time() < deadline and any(counts().get(s, 0) < 4 for s in ("traces", "metrics", "logs")):
            time.sleep(0.1)
        retry_counts = counts()
        retry_expected = {"traces": 8, "metrics": 4, "logs": 4}
        expect(all(retry_counts.get(s, 0) == n for s, n in retry_expected.items()), f"retry counts {retry_counts}")

        # A persistent sink failure must not be acknowledged as successful by Collector.
        requests.post(f"{RECEIVER_URL}/__control/storage-unavailable", timeout=2).raise_for_status()
        with sqlite3.connect(DB) as cx:
            valid_trace = cx.execute("SELECT payload FROM payloads WHERE signal='traces' LIMIT 1").fetchone()[0]
        storage_failure = requests.post(f"{COLLECTOR_URL}/v1/traces", data=valid_trace,
                                        headers={"Content-Type": "application/x-protobuf"}, timeout=15)
        outcomes["cases"].append({"case": "storage-failure", "http_status": storage_failure.status_code})
        expect(storage_failure.status_code >= 500, f"storage outage was acknowledged: {storage_failure.status_code}")
        requests.post(f"{RECEIVER_URL}/__control/storage-available", timeout=2).raise_for_status()
        expect(counts() == retry_counts, "storage failure created records")

        # Restart the receiver against the same SQLite path and verify committed counts.
        receiver.terminate()
        receiver.wait(timeout=10)
        receiver = subprocess.Popen([sys.executable, str(RECEIVER)], cwd=ATTEMPT, env=env,
                                    stdout=receiver_log, stderr=subprocess.STDOUT)
        wait_port(9000, receiver, ATTEMPT / "receiver.log")
        after_restart = counts()
        expect(after_restart == retry_counts, f"counts changed after restart: {after_restart}")

        # Verify known fields in the decoded durable records.
        all_records = records()
        expect(len(all_records) == 16, f"expected 16 accepted signal payloads, got {len(all_records)}")
        for signal, payload in all_records:
            blob = json.dumps(payload, sort_keys=True)
            expect("dce-e005-checkout" in blob, f"resource identity missing in {signal}")
        metric_payloads = [p for s, p in all_records if s == "metrics"]
        expect(all("dce.e005.requests" in json.dumps(p) and '"unit": "1"' in json.dumps(p) and '"as_int": "7"' in json.dumps(p)
                   for p in metric_payloads), "metric name/unit/value fidelity failed")
        source_metric_points = sorted(
            (p["name"], p["unit"], p["value"], p["time_unix_nano"])
            for p in METRIC_SOURCE_POINTS
        )
        sink_metric_points = sorted(
            (metric.get("name", ""), metric.get("unit", ""), str(point.get("as_int", "")),
             str(point.get("time_unix_nano", "")))
            for payload in metric_payloads
            for resource_metrics in payload.get("resource_metrics", [])
            for scope_metrics in resource_metrics.get("scope_metrics", [])
            for metric in scope_metrics.get("metrics", [])
            if metric.get("name") == "dce.e005.requests"
            for point in metric.get("sum", {}).get("data_points", [])
        )
        expect(len(source_metric_points) == 4, f"SDK source metric points: {source_metric_points}")
        expect(source_metric_points == sink_metric_points,
               f"exact metric source/sink mismatch: source={source_metric_points}; sink={sink_metric_points}")
        outcomes["metric_source_points"] = METRIC_SOURCE_POINTS
        outcomes["metric_timestamp_source_sink_match"] = True
        trace_payloads = [p for s, p in all_records if s == "traces"]
        span_names = {span["name"] for p in trace_payloads
                      for resource_spans in p.get("resource_spans", [])
                      for scope_spans in resource_spans.get("scope_spans", [])
                      for span in scope_spans.get("spans", [])}
        expect({"checkout", "inventory.lookup"}.issubset(span_names), f"trace/span fidelity failed: {span_names}")
        log_payloads = [p for s, p in all_records if s == "logs"]
        expect(all("controlled checkout accepted" in json.dumps(p) and "event.name" in json.dumps(p) for p in log_payloads), "log fidelity failed")
        outcomes.update({"status": "PASS", "counts": after_restart, "durable_records": len(all_records)})
    except Exception as exc:
        outcomes.update({"status": "FAIL", "error": f"{type(exc).__name__}: {exc}", "counts": counts() if DB.exists() else {}})
        raise
    finally:
        if collector is not None:
            collector.terminate()
            collector.wait(timeout=10)
        if receiver.poll() is None:
            receiver.terminate()
            receiver.wait(timeout=10)
        collector_log.close()
        receiver_log.close()
        (ATTEMPT / "summary.json").write_text(json.dumps(outcomes, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(outcomes, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
