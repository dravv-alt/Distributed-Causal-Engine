# E005-R002 updated review proposal

**Review status:** pending. This proposal supplements, and does not replace, the earlier review proposal or the E005 decision record.

## Question for review

Does the completed OpenResearch-managed E005-R002 run provide enough evidence to accept the local synthetic telemetry-attachment contract for XP002, and permit progression to the separately registered next scope?

## Evidence added since the earlier proposal

- OpenResearch local run `c6653066-db74-4152-abf8-3e74efdc6147` completed on frozen source commit `1f4591d6081a54588a1dde01152ce0a829848b57` using the registered fixed command and local backend with telemetry disabled.
- Its preflight records a loopback-only, synthetic-fixture boundary with no external requests. No remote compute or telemetry upload was used.
- The saved summary reports three successful valid fixture rounds; malformed trace, metric and log requests returned 400 without writes; transient retry recovered; injected storage failure returned 503; and 16 durable payloads remained (8 traces, 4 metrics, 4 logs).
- Four SDK metric source tuples match the durable sink on name, unit, value and timestamp. The read-only artifact audit independently passed all 13 checks, including SQLite integrity.
- The frozen runner restarts the receiver and asserts the durable counts are unchanged before it writes final `PASS`. The independent audit does not independently reconstruct that restart event from a restart log; the assertion and final status are runner evidence.
- The first OpenResearch attempt failed before test cases because local port 9101 was occupied. That failure is retained separately; the successful retry used the same frozen node/source and protocol after the port was free.

## Proposed bounded interpretation

**Proposed outcome: PROCEED for XP002's local synthetic ingestion contract only.** E005-R001 demonstrated delivery, malformed-input handling, retries, storage-failure behavior and restart retention, but left exact metric timestamp fidelity unknown. E005-R002 captured timestamps before export and matched all four source points to the durable sink under the OpenResearch local runner. Taken together, these runs support the registered local ingestion behavior within the tested fixtures.

This proposal does not establish broad production telemetry coverage, load capacity, real-service instrumentation quality, RCA accuracy, neuro-symbolic benefit, causality or remediation safety. It does not turn the nine-case E006 sample into full XP003 coverage. XP003's descriptive scan remains limited to the 19 files and nine frozen RCAEval cases documented in its own run record.

## Requested human decision

Review the bounded PROCEED proposal for XP002 and specify the next permitted scope. The permanent E005 decision remains unchanged until an explicit review is recorded through a separately authorized additive record. The execution plan currently still lists XP002 and XP003 as `planned_not_authorized` despite the additive E005/E006 registration amendments; this status conflict must be reconciled before later stages are advanced.
