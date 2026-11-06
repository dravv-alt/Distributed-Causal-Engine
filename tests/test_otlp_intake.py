import asyncio
from pathlib import Path

import httpx
import pytest
from google.rpc import status_pb2
from opentelemetry.proto.collector.metrics.v1 import metrics_service_pb2
from opentelemetry.proto.collector.trace.v1 import trace_service_pb2
from opentelemetry.proto.common.v1 import common_pb2
from opentelemetry.proto.metrics.v1 import metrics_pb2
from opentelemetry.proto.resource.v1 import resource_pb2
from opentelemetry.proto.trace.v1 import trace_pb2

from dce_foundation.ingest.app import PROTOBUF_CONTENT_TYPE, create_app
from dce_foundation.ingest.otlp import decode_metadata, replay_evidence
from dce_foundation.ingest.store import IntakeStore, StoreUnavailable


def resource(service_name="checkout"):
    return resource_pb2.Resource(attributes=[common_pb2.KeyValue(
        key="service.name", value=common_pb2.AnyValue(string_value=service_name)
    )])


def metric_payload():
    request = metrics_service_pb2.ExportMetricsServiceRequest()
    resource_metrics = request.resource_metrics.add(resource=resource())
    scope_metrics = resource_metrics.scope_metrics.add()
    metric = scope_metrics.metrics.add(name="demo.requests", unit="{request}")
    point = metric.sum.data_points.add(as_int=1, time_unix_nano=1_700_000_000_000_000_000)
    point.attributes.add(key="route", value=common_pb2.AnyValue(string_value="/checkout"))
    metric.sum.aggregation_temporality = metrics_pb2.AGGREGATION_TEMPORALITY_CUMULATIVE
    metric.sum.is_monotonic = True
    return request.SerializeToString()


def trace_payload():
    request = trace_service_pb2.ExportTraceServiceRequest()
    resource_spans = request.resource_spans.add(resource=resource())
    scope_spans = resource_spans.scope_spans.add()
    span = scope_spans.spans.add(name="checkout.request", trace_id=b"a" * 16, span_id=b"b" * 8,
                                 parent_span_id=b"c" * 8, start_time_unix_nano=1_700_000_000_000_000_001,
                                 end_time_unix_nano=1_700_000_000_000_000_123)
    span.kind = trace_pb2.Span.SPAN_KIND_SERVER
    return request.SerializeToString()


async def request(app, method, path, content=b"", headers=None):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://dce.test") as client:
        return await client.request(method, path, content=content, headers=headers)


def post(app, path, payload, content_type=PROTOBUF_CONTENT_TYPE):
    return asyncio.run(request(app, "POST", path, payload, {"content-type": content_type}))


def test_metadata_preserves_source_identity_event_time_and_signal():
    metrics = decode_metadata("metrics", metric_payload())
    traces = decode_metadata("traces", trace_payload())
    assert metrics.source_identities == ("checkout",)
    assert metrics.item_count == 1
    assert metrics.event_time_min_unix_nano == 1_700_000_000_000_000_000
    assert traces.source_identities == ("checkout",)
    assert traces.item_count == 1
    assert traces.event_time_max_unix_nano == 1_700_000_000_000_000_123
    assert replay_evidence("metrics", metric_payload())["metrics"] == [{
        "service_name": "checkout", "name": "demo.requests", "unit": "{request}",
        "data_type": "sum", "aggregation_temporality": 2, "is_monotonic": True,
    }]
    span = replay_evidence("traces", trace_payload())["spans"][0]
    assert span["trace_id"] == (b"a" * 16).hex()
    assert span["span_id"] == (b"b" * 8).hex()
    assert span["parent_span_id"] == (b"c" * 8).hex()


def test_otlp_success_is_protocol_response_and_durable(tmp_path):
    database = tmp_path / "intake.sqlite3"
    app = create_app(database)
    metric_response = post(app, "/v1/metrics", metric_payload())
    trace_response = post(app, "/v1/traces", trace_payload())
    assert metric_response.status_code == trace_response.status_code == 200
    assert metric_response.headers["content-type"].startswith(PROTOBUF_CONTENT_TYPE)
    assert not metrics_service_pb2.ExportMetricsServiceResponse.FromString(metric_response.content).HasField("partial_success")
    assert not trace_service_pb2.ExportTraceServiceResponse.FromString(trace_response.content).HasField("partial_success")
    # A new store instance proves persistence across the process/app lifetime.
    replay = IntakeStore(database).replay()
    assert [batch.sequence for batch in replay] == [1, 2]
    assert [batch.signal for batch in replay] == ["metrics", "traces"]
    assert replay[0].source_identities == ("checkout",)
    assert replay[0].event_time_min_unix_nano == 1_700_000_000_000_000_000
    assert replay[1].event_time_max_unix_nano == 1_700_000_000_000_000_123
    assert replay[1].payload is None
    raw_replay = IntakeStore(database).replay(include_payload=True)
    assert replay_evidence(raw_replay[0].signal, raw_replay[0].payload)["metrics"][0]["unit"] == "{request}"


def test_duplicate_payload_is_preserved_and_reported(tmp_path):
    app = create_app(tmp_path / "intake.sqlite3")
    payload = metric_payload()
    assert post(app, "/v1/metrics", payload).status_code == 200
    assert post(app, "/v1/metrics", payload).status_code == 200
    batches = app.state.store.replay()
    assert [batch.sequence for batch in batches] == [1, 2]
    assert batches[1].duplicate_of_sequence == 1
    assert app.state.store.stats()["duplicates"] == 1


@pytest.mark.parametrize("path,payload,content_type,status", [
    ("/v1/metrics", b"not protobuf", PROTOBUF_CONTENT_TYPE, 400),
    ("/v1/metrics", metric_payload(), "application/json", 415),
])
def test_bad_input_returns_non_retryable_protobuf_status(tmp_path, path, payload, content_type, status):
    app = create_app(tmp_path / "intake.sqlite3")
    response = post(app, path, payload, content_type)
    assert response.status_code == status
    assert response.headers["content-type"].startswith(PROTOBUF_CONTENT_TYPE)
    assert status_pb2.Status.FromString(response.content).message
    assert app.state.store.stats()["accepted"] == 0


def test_payload_limit_returns_explicit_error(tmp_path):
    app = create_app(tmp_path / "intake.sqlite3", max_payload_bytes=4)
    response = post(app, "/v1/metrics", metric_payload())
    assert response.status_code == 413
    assert app.state.store.stats()["accepted"] == 0


def test_storage_failure_never_acknowledges_success(tmp_path, monkeypatch):
    app = create_app(tmp_path / "intake.sqlite3")
    monkeypatch.setattr(app.state.store, "append", lambda *_: (_ for _ in ()).throw(StoreUnavailable("test storage outage")))
    response = post(app, "/v1/metrics", metric_payload())
    assert response.status_code == 503
    assert status_pb2.Status.FromString(response.content).message == "test storage outage"
    assert app.state.store.stats()["accepted"] == 0


def test_health_reports_intake_storage(tmp_path):
    app = create_app(tmp_path / "intake.sqlite3")
    response = asyncio.run(request(app, "GET", "/healthz"))
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["storage"]["accepted"] == 0
