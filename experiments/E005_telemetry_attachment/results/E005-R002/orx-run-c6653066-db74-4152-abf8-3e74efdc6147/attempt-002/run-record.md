# E005-R002 OpenResearch local run record

- Permanent experiment/run: E005-R002, ORX attempt 002
- OpenResearch run: `c6653066-db74-4152-abf8-3e74efdc6147`
- Local project node: `3e0b58bd-062b-45eb-9fcb-c2e88a7c8804` (frozen, idle after completion)
- Frozen source commit: `1f4591d6081a54588a1dde01152ce0a829848b57`
- Fixed command: `python experiments/E005_telemetry_attachment/run_e005_r002.py`
- Backend: local; telemetry setting: off
- Execution boundary recorded by preflight: loopback only, synthetic fixtures, no external requests
- Outcome: runner PASS; 3 valid rounds, malformed requests rejected without writes, transient retry succeeded, storage failure returned 503, and four metric source timestamps matched four durable sink timestamps.
- Durable records: 8 traces, 4 metrics, 4 logs (16 total); SQLite integrity check: `ok`.
- Independent audit: [independent-audit.json](independent-audit.json), all 13 checks passed.
- Run log: local ORX log copied as `orx-run.log`; collector log: `collector.log`.

## Evidence file SHA-256

| File | SHA-256 |
|---|---|
| `collector.log` | `7ba7f7219f2986f6c91435359ea0c0d9095dde9402c3d38e022c724955fa4ceb` |
| `independent-audit.json` | `d63d5de6922f56d51c2a06f201eaaef5d2d3683fc24bd307753be7910b0c5473` |
| `preflight.json` | `4fd9934f7eea37bc7a1b65845a658b5a86e5fda24215e7c4d2bc31231cb146c5` |
| `summary.json` | `23e48f830989d93e7a39d9c7a0bf31951390ac39c9c1b3ad2a792b8c0046bd10` |
| `telemetry.sqlite` | `681be461bb27d67ed697b38c0a9cffbc4c3e9dac31ee53cabff99344a6dae4ef` |
| `orx-run.log` | `416342178fdde1054c2bb69adb3c5f377218134af7510884905aa2263efce63b` |

## Interpretation and limits

This confirms local synthetic telemetry attachment and timestamp fidelity for this frozen E005-R002 fixture. It does not establish real-service coverage, telemetry quality in production, RCA accuracy, causal validity, or overall XP002/E005 acceptance. The prior ORX attempt at [the original failed attempt record](../../attempt-002/run-record.md) failed before processing cases because loopback port 9101 was occupied; that failure record remains intact. This successful retry used the same node, source commit, command, and protocol after the port was free. E005 review status remains unchanged pending the designated review.
