# E035-R001 protocol (frozen before execution)

Date: 2026-11-07. Planning reference: XP032. Authorization: user explicitly instructed the agent to overrule pending gates and proceed; this additive record documents that instruction. This does not alter or erase the E003 pending review finding.

## Question and design

Challenge a deterministic offline plan checker with 500 proposals: 100 valid, 100 availability violations, 100 replica violations, 100 risk violations, and 100 combined violations. Each proposal carries only its plan and declared constraint values. Expected classes are stored in a separate evaluator-only file and are never loaded by the checker.

Checker rule: reject if projected availability is below its minimum, projected replicas are below the minimum, or risk exceeds the maximum. Otherwise accept. No actions are executed; collateral effects from execution are therefore out of scope and recorded as not measured, not zero.

## Measures and controls

Report unsafe acceptance rate, refusal correctness on invalid proposals, valid-plan acceptance, and confusion counts. No numeric acceptance thresholds are specified in the XP032 card; do not invent one or label the result a pass. Deterministic generated fixtures, one checker version, no random seed, evaluator labels separated from inference inputs. Independent audit recomputes classifications from fixture constraints using a separate implementation.

## Limits

Synthetic values and a simple fixed policy; no application integration, action executor, service state, workload, or real collateral-effect measurement. The run can expose checker/fixture agreement only.
