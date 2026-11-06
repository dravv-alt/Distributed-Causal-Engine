"""Loopback-only OTLP/HTTP receiver and durable SQLite sink for E005."""
from __future__ import annotations

import hashlib
import gzip
import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceRequest
from opentelemetry.proto.collector.logs.v1.logs_service_pb2 import ExportLogsServiceResponse
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import ExportMetricsServiceRequest
from opentelemetry.proto.collector.metrics.v1.metrics_service_pb2 import ExportMetricsServiceResponse
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceRequest
from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import ExportTraceServiceResponse
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import DecodeError

PORT = int(os.environ.get("E005_RECEIVER_PORT", "9000"))
DB = Path(os.environ.get("E005_DB", "e005-telemetry.sqlite"))
SCHEMAS = {
    "/v1/traces": (ExportTraceServiceRequest, ExportTraceServiceResponse, "traces"),
    "/v1/metrics": (ExportMetricsServiceRequest, ExportMetricsServiceResponse, "metrics"),
    "/v1/logs": (ExportLogsServiceRequest, ExportLogsServiceResponse, "logs"),
}


def connect() -> sqlite3.Connection:
    cx = sqlite3.connect(DB, timeout=10)
    cx.execute("PRAGMA synchronous=FULL")
    cx.execute("PRAGMA journal_mode=WAL")
    cx.execute("CREATE TABLE IF NOT EXISTS payloads (id INTEGER PRIMARY KEY, signal TEXT NOT NULL, sha256 TEXT NOT NULL, payload BLOB NOT NULL, decoded_json TEXT NOT NULL)")
    cx.execute("CREATE TABLE IF NOT EXISTS controls (name TEXT PRIMARY KEY, value INTEGER NOT NULL)")
    cx.commit()
    return cx


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def send(self, code: int, body: bytes = b"") -> None:
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Type", "application/x-protobuf")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path == "/__control/fail-next-write":
            with connect() as cx:
                cx.execute("INSERT INTO controls(name,value) VALUES('fail_next',1) ON CONFLICT(name) DO UPDATE SET value=1")
            return self.send(200)
        if self.path == "/__control/storage-unavailable":
            with connect() as cx:
                cx.execute("INSERT INTO controls(name,value) VALUES('storage_offline',1) ON CONFLICT(name) DO UPDATE SET value=1")
            return self.send(200)
        if self.path == "/__control/storage-available":
            with connect() as cx:
                cx.execute("DELETE FROM controls WHERE name='storage_offline'")
            return self.send(200)
        schema = SCHEMAS.get(self.path)
        if schema is None:
            return self.send(404)
        request_type, response_type, signal = schema
        try:
            n = int(self.headers.get("Content-Length", "-1"))
            if n < 0 or n > 10_000_000:
                return self.send(413)
            raw = self.rfile.read(n)
            if self.headers.get("Content-Encoding", "").lower() == "gzip":
                raw = gzip.decompress(raw)
            message = request_type()
            message.ParseFromString(raw)
            decoded = MessageToDict(message, preserving_proto_field_name=True)
        except (ValueError, DecodeError, OSError) as exc:
            print(f"invalid {self.path} content-type={self.headers.get('Content-Type')} encoding={self.headers.get('Content-Encoding')} bytes={n if 'n' in locals() else 'unknown'} error={type(exc).__name__}:{exc}", flush=True)
            return self.send(400)
        except Exception as exc:
            print(f"reject {self.path} unexpected={type(exc).__name__}:{exc}", flush=True)
            return self.send(400)
        try:
            with connect() as cx:
                should_fail = cx.execute("SELECT value FROM controls WHERE name='fail_next'").fetchone()
                storage_offline = cx.execute("SELECT value FROM controls WHERE name='storage_offline'").fetchone()
                if storage_offline and storage_offline[0]:
                    return self.send(503)
                if should_fail and should_fail[0]:
                    cx.execute("DELETE FROM controls WHERE name='fail_next'")
                    cx.commit()
                    return self.send(503)
                cx.execute("INSERT INTO payloads(signal,sha256,payload,decoded_json) VALUES(?,?,?,?)",
                           (signal, hashlib.sha256(raw).hexdigest(), raw,
                            json.dumps(decoded, sort_keys=True, separators=(",", ":"))))
                cx.commit()
        except sqlite3.Error:
            return self.send(503)
        return self.send(200, response_type().SerializeToString())

    def do_GET(self) -> None:
        if self.path != "/__admin/counts":
            return self.send(404)
        with connect() as cx:
            counts = dict(cx.execute("SELECT signal,COUNT(*) FROM payloads GROUP BY signal").fetchall())
        body = json.dumps(counts, sort_keys=True).encode()
        self.send_response(200)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, _format: str, *_args: object) -> None:
        return

    def log_error(self, format: str, *args: object) -> None:
        print(format % args, flush=True)


if __name__ == "__main__":
    if DB.exists():
        with connect():
            pass
    else:
        with connect():
            pass
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
