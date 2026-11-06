# Source-provenance inventory — fixed scope before inspection

Date: 4 November 2026 (Asia/Calcutta). Authority: user's instruction to proceed with the deterministic next step described on 8 October 2026. This is a read-only evidence-qualification activity. It is not an experiment, detector implementation, E005 registration, or execution.

## Question

Can authoritative, version-linked records establish semantic provenance for the sampled metrics and identify a documented healthy-control or independent evaluation population?

## Fixed inputs

Use only the eight source entries and their preselected metric names in `docs/research-design/2026-10-08-bounded-acquisition/sample-plan.json`. Deduplicate identical Market metric names across the two Market scenarios: there are 18 distinct candidate names.

Read only:

1. Existing local manifests, retained profiles, prior bounded-acquisition records, and experiment provenance records. No raw archive or retained telemetry payload access.
2. The already archived Microsoft/OpenRCA commit `c1bd4af7f635171a1c31cdd567c07d698dff6abc` and, at most, twelve official source-owner documentation/code URLs discovered from it or from the exporter project named by a metric. Each source is retained as URL, retrieval time, content hash and concise evidence excerpt/reference. Do not treat an upstream source as the local data source unless a version/configuration link supports that claim.

For each candidate, record separately: local source path/header occurrence; meaning; unit; kind; temporality; aggregation; reset behavior; exporter/configuration and transformation provenance; dataset-version match; and support status. `UNKNOWN` is the required value when the field is unsupported.

## Exclusions

- No raw ZIP extraction, telemetry scan, SQLite payload read, metrics calculation, threshold, model, ranking, or detector.
- No fault/root/query labels, schedules, outcomes, or source prompts used to select metrics or infer healthy state.
- No inference from metric-name resemblance, a source example, low values, pre-fault time, absence of logs, or missing records.
- No alteration of existing records, registries, source, or artifacts.

## Stop and report

Stop after a single inventory report. Answer only whether (a) any sampled metric is fully semantically qualified, (b) a healthy-control source is documented, and (c) an independent evaluation population is documented. Do not extend inspection to new metrics or sources if the answer is negative.

The next action after this package remains a human review of the evidence. It cannot register or execute a successor experiment by itself.
