# P20 synthesis update — XP001 review and XP002 execution

Date: 2026-11-08

This additive update records the latest reviewed E003 finding and E005 telemetry-attachment evidence. Prior experiment records and P20 snapshots remain unchanged.

## XP001 / E003

The project owner accepted the bounded census/replay finding and explicitly retained E003's **REVISE** outcome. The review record is `2026-11-08-e003-bounded-census-review.md`. The 162 V004 profile records match manifest metadata under the new read-only reconciliation; raw ZIP bytes were unavailable for independent hash recomputation. V006 reports 335 cases verified in each of two replays. E003 is not an overall adequacy or RCA-readiness pass.

## XP002 / E005

E005-R001's tested local delivery behavior was bounded and successful, but its preregistered exact metric source-to-sink timestamp criterion remained unknown. E005-R002's standalone local attempt captured and matched all four SDK metric tuples against the durable SQLite sink. A separate read-only artifact check confirmed the saved tuples, counts and SQLite integrity; source-manifest file hashes matched.

The first OpenResearch-managed local attempt (ORX run `01e74150-4301-4a56-b422-e29efea2a886`, source commit `1f4591d`) failed before any telemetry case ran: the Collector's internal Prometheus endpoint could not bind `127.0.0.1:9101`, which was held by an unrelated Dart DevTools process. The failure is recorded in `E005-R002/attempt-002/run-record.md`; it is an environment failure, not a telemetry result.

**XP002 remains incomplete.** The standalone R002 evidence does not substitute for the protocol's OpenResearch-managed execution. No RCA, neuro-symbolic, production, or remote-execution claim follows. The failed ORX node can be retried unchanged after the port is available; no process was stopped and no existing protocol/configuration/source was altered.

## Campaign state

XP001's bounded review is recorded while E003 remains REVISE. XP002 is the current stage and awaits a successful local ORX run and human review. Later dependent stages have not been advanced by this update.
