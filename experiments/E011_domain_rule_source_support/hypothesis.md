# Hypothesis

## Question

Do the nine selected blind RCAEval cases expose literal source fields or log text that could supply the three predicates in the XP008 illustrative database rule?

## Hypothesis

At least one candidate predicate may appear in a telemetry field name or log message. A literal match is only source availability; it does not establish the signal's semantics, truth, entity linkage, causal meaning, or predictive utility.

## Variables and measures

- Input: fixed nine inference-only case directories referenced by E010.
- Audit categories: literal database saturation/overload, connection-pool saturation/exhaustion, latency, and service identity terms.
- Outputs: per-case and aggregate row counts for telemetry modalities and keyword matches; SHA-256 for every input file.
- Controls: no evaluator-only directory, label, fault schedule, or scoring point is read; no model tuning or inference is performed.

## Decision boundary

This audit cannot establish XP008 localization delta or rule/path accuracy. Any absent, ambiguous, or unqualified predicate remains unavailable/UNKNOWN for a real diagnosis comparison.
