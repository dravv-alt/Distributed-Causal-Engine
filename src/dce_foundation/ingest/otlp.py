"""Strict OTLP protobuf decoding and source metadata extraction.

This module preserves transport payloads. It does not convert OTLP telemetry into
model features or infer units, topology, metric meanings, or causal relations.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Literal

from google.protobuf.message import DecodeError
from opentelemetry.proto.collector.metrics.v1 import metrics_service_pb2
from opentelemetry.proto.collector.trace.v1 import trace_service_pb2

Signal = Literal["metrics", "traces"]


class OtlpDecodeError(ValueError):
    """The payload cannot be decoded as the declared OTLP signal."""


@dataclass(frozen=True)
class BatchMetadata:
    signal: Signal
    payload_sha256: str
    source_identities: tuple[str, ...]
    event_time_min_unix_nano: int | None
    event_time_max_unix_nano: int | None
    item_count: int
    resource_count: int
    summary_json: str


def _any_value(value) -> str:
    kind = value.WhichOneof("value")
    if kind is None:
        return ""
    scalar = getattr(value, kind)
    if kind == "bytes_value":
        return scalar.hex()
    if kind == "array_value":
        return json.dumps([_any_value(item) for item in scalar.values], separators=(",", ":"))
    if kind == "kvlist_value":
        return json.dumps({item.key: _any_value(item.value) for item in scalar.values}, sort_keys=True, separators=(",", ":"))
    return str(scalar)


def _service_identity(resource) -> str:
    attributes = {item.key: _any_value(item.value) for item in resource.attributes}
    # service.name is an OTel resource identity. Missing identity remains explicit.
    return attributes.get("service.name") or "UNKNOWN_SERVICE"


def _parse(signal: Signal, payload: bytes):
    request = metrics_service_pb2.ExportMetricsServiceRequest() if signal == "metrics" else trace_service_pb2.ExportTraceServiceRequest()
    try:
        request.ParseFromString(payload)
    except DecodeError as exc:
        raise OtlpDecodeError(f"invalid OTLP {signal} protobuf") from exc
    # ParseFromString accepts arbitrary valid protobuf fields. A payload with no
    # matching root fields is valid as an empty OTLP request, which OTLP allows.
    return request


def _metadata_metrics(request, payload: bytes) -> BatchMetadata:
    identities: set[str] = set()
    times: list[int] = []
    count = 0
    for resource_metrics in request.resource_metrics:
        identities.add(_service_identity(resource_metrics.resource))
        for scope_metrics in resource_metrics.scope_metrics:
            for metric in scope_metrics.metrics:
                data = metric.WhichOneof("data")
                if data is None:
                    continue
                points = getattr(metric, data).data_points
                count += len(points)
                for point in points:
                    if point.time_unix_nano:
                        times.append(point.time_unix_nano)
    summary = {"signal": "metrics", "resource_count": len(request.resource_metrics), "data_points": count}
    return BatchMetadata("metrics", sha256(payload).hexdigest(), tuple(sorted(identities)), min(times) if times else None,
                         max(times) if times else None, count, len(request.resource_metrics), json.dumps(summary, sort_keys=True))


def _metadata_traces(request, payload: bytes) -> BatchMetadata:
    identities: set[str] = set()
    times: list[int] = []
    count = 0
    span_links = 0
    for resource_spans in request.resource_spans:
        identities.add(_service_identity(resource_spans.resource))
        for scope_spans in resource_spans.scope_spans:
            count += len(scope_spans.spans)
            for span in scope_spans.spans:
                if span.start_time_unix_nano:
                    times.append(span.start_time_unix_nano)
                if span.end_time_unix_nano:
                    times.append(span.end_time_unix_nano)
                span_links += len(span.links)
    summary = {"signal": "traces", "resource_count": len(request.resource_spans), "spans": count, "span_links": span_links}
    return BatchMetadata("traces", sha256(payload).hexdigest(), tuple(sorted(identities)), min(times) if times else None,
                         max(times) if times else None, count, len(request.resource_spans), json.dumps(summary, sort_keys=True))


def decode_metadata(signal: Signal, payload: bytes) -> BatchMetadata:
    request = _parse(signal, payload)
    return _metadata_metrics(request, payload) if signal == "metrics" else _metadata_traces(request, payload)


def success_response(signal: Signal) -> bytes:
    response = metrics_service_pb2.ExportMetricsServiceResponse() if signal == "metrics" else trace_service_pb2.ExportTraceServiceResponse()
    return response.SerializeToString()


def replay_evidence(signal: Signal, payload: bytes) -> dict:
    """Return a bounded human-readable view while the original payload stays durable.

    This is an inspection projection, not a canonical mapper. It intentionally
    exposes names, units, aggregation fields and trace/span links without
    translating them into DCE features or relations.
    """
    request = _parse(signal, payload)
    if signal == "metrics":
        metrics = []
        for resource_metrics in request.resource_metrics:
            service = _service_identity(resource_metrics.resource)
            for scope_metrics in resource_metrics.scope_metrics:
                for metric in scope_metrics.metrics:
                    data = metric.WhichOneof("data")
                    item = {"service_name": service, "name": metric.name, "unit": metric.unit or None, "data_type": data}
                    if data in {"sum", "histogram", "exponential_histogram"}:
                        item["aggregation_temporality"] = getattr(metric, data).aggregation_temporality
                    if data == "sum":
                        item["is_monotonic"] = metric.sum.is_monotonic
                    metrics.append(item)
        return {"metrics": metrics}
    spans = []
    for resource_spans in request.resource_spans:
        service = _service_identity(resource_spans.resource)
        for scope_spans in resource_spans.scope_spans:
            for span in scope_spans.spans:
                spans.append({"service_name": service, "name": span.name, "trace_id": span.trace_id.hex(),
                              "span_id": span.span_id.hex(), "parent_span_id": span.parent_span_id.hex() or None,
                              "start_time_unix_nano": span.start_time_unix_nano or None,
                              "end_time_unix_nano": span.end_time_unix_nano or None, "kind": span.kind})
    return {"spans": spans}


def request_type(signal: Signal):
    return metrics_service_pb2.ExportMetricsServiceRequest if signal == "metrics" else trace_service_pb2.ExportTraceServiceRequest
