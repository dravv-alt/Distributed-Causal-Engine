# Telemetry contract

Required envelope: schema_version, event_id, environment_id, service_id, optional instance_id,
observed_at, received_at, source and quality flags. Each measurement declares name, value, unit and kind.
Counter temporality/reset behavior and histogram boundaries must survive mapping. Never average instance percentiles as a global percentile.

Feature mappings declare source metrics, canonical units, aggregation cadence and missingness. Keep raw values separate
from normalized features. Schema order, service mapping and preprocessing are part of the model compatibility contract.

R0 features are latency_ms (ms), error_rate (ratio), request_rate (req/s), cpu_util (ratio).
R0 accepts offline array datasets, not OTLP or live JSON ingestion. Proposed adapters require integration experiments.
Store schema definitions in data/schemas and artifact metadata in data/manifests; no fabricated schema-version compatibility.
