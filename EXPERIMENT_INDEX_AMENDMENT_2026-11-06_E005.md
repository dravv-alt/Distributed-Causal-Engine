# Permanent register amendment: E005

Date: 2026-11-06 (Asia/Calcutta). Authority: the user's instruction to proceed through the planned experiments sequentially and implement them to evaluate neuro-symbolic RCA effectiveness, including despite E004's REVISE result.

This additive amendment allocates E005 only. It does not edit the permanent index or prior evidence, approve E001-E004 outcomes, pass an earlier gate, or authorize later experiments. The E005 scope uses a locally generated controlled workload because the inherited OpenRCA metric semantics and exact release identity remain unresolved.

| ID | Purpose | Registered scope | Evidence |
|---|---|---|---|
| E005 | Controlled telemetry attachment | Verify an instrumented local workload's OTLP telemetry reaches DCE's receiver with identity, units, timestamps and resource attributes preserved, and that acknowledgments reflect validation and durable storage. | `experiments/E005_telemetry_attachment/` |

Question: does the local telemetry path preserve known OpenTelemetry metric, trace and log fields and handle malformed payloads, transient rejection/retry, and receiver restart without acknowledging undurable data?

Planning alignment: XP002 (Telemetry attachment), as the first unallocated planned capability after the existing representation and structural baseline work. The historical XP source label is not an experiment identity.

Run identity: E005-R001. The protocol must be frozen before implementation or execution. This experiment evaluates ingestion correctness only; it does not test RCA accuracy, hybrid superiority, causal reasoning, alerting or remediation.

The user's instruction authorizes proceeding through experiments one at a time. Every later experiment still requires its own registered scope and protocol. No successor is allocated here.
