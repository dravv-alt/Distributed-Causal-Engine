"""Emit one known metric and one request span directly to DCE's OTLP/HTTP intake."""
from __future__ import annotations

import os

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor


endpoint = os.environ.get("DCE_OTLP_ENDPOINT", "http://127.0.0.1:4318")
resource = Resource.create({"service.name": "dce-demo-service", "service.instance.id": "demo-1"})
metric_reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=f"{endpoint}/v1/metrics"), export_interval_millis=200)
meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
metrics.set_meter_provider(meter_provider)
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")))
trace.set_tracer_provider(tracer_provider)

meter = metrics.get_meter("dce.demo")
counter = meter.create_counter("dce.demo.requests", unit="{request}", description="Known demo counter")
tracer = trace.get_tracer("dce.demo")

with tracer.start_as_current_span("demo.request") as span:
    span.set_attribute("dce.demo", True)
    counter.add(1, {"route": "/demo"})

meter_provider.force_flush()
tracer_provider.force_flush()
meter_provider.shutdown()
tracer_provider.shutdown()
print("Sent known metric dce.demo.requests ({request}) and trace span demo.request")
