# E005 hypothesis

## Research question

Can a local instrumented service send known metrics, traces and logs through an OTLP/HTTP pipeline into DCE such that field identity and values survive, malformed requests are rejected, and successful acknowledgments occur only after durable storage?

## Hypothesis

For the preregistered deterministic fixtures, DCE will preserve every declared resource attribute, signal identity, timestamp, unit and value; reject malformed payloads without creating records; retry a controlled transient failure without losing valid telemetry; and retain acknowledged records after receiver restart.

## Scope boundary

The independent variable is the delivery condition: valid first attempt, malformed request, controlled transient server rejection followed by retry, or receiver restart after acknowledgment. The dependent outcomes are field-level fidelity, response status, durable record count and post-restart recovery. There is no detector, root-cause ranking, fault label, causal claim, alert, or remediation action in this experiment.

## Evidence boundary

Fixtures are synthetic and generated locally. Their intended units and timestamps are known by construction; they do not qualify similarly named OpenRCA metrics. A successful result would establish only the tested ingestion path and tested fields for the frozen software versions and configuration.
