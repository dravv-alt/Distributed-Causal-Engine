# E005-R002 ORX attempt 002

Date: 2026-11-08
OpenResearch run: `01e74150-4301-4a56-b422-e29efea2a886`
ORX experiment node: `3e0b58bd-062b-45eb-9fcb-c2e88a7c8804`
Source commit: `1f4591d6081a54588a1dde01152ce0a829848b57`
Backend: local
Outcome: environment failure before any telemetry case ran

The frozen runner started the receiver but the OpenTelemetry Collector exited during startup because its internal Prometheus exporter could not bind `127.0.0.1:9101` (`address already in use`). Read-only inspection identified an unrelated Dart DevTools process holding that loopback port. No process was stopped. The runner recorded `status=FAIL` with an empty case list and zero accepted counts. This is an environment failure, not a result on telemetry fidelity.

The failed attempt's artifacts are retained in this directory. `orx-run.log` contains machine-local paths and is retained locally; it should not be published. The Collector log contains the bind error. The attempt did not access external endpoints; its Collector and receiver endpoints are configured on loopback.

## Hashes

SHA-256 values from the preserved files:

| File | SHA-256 |
|---|---|
| `collector.log` | `8eba5141f80873c71989aa0426bac88c196fd5bbf2d2294abf369eebe04f1f7a` |
| `orx-run.log` | `b501c1332e7673347fc3d01bb765de2d34e97867d53faf8be17b82f9fe06c4ab` |
| `preflight.json` | `4fd9934f7eea37bc7a1b65845a658b5a86e5fda24215e7c4d2bc31231cb146c5` |
| `receiver.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `summary.json` | `5dfc77d7678ff3cd3a449e8a0c043ba019db08dac146d7c55ed8b8314fc7001c` |
| `telemetry.sqlite` | `e09192810fb6484ad1781671a9799cd1e27ebb95a98f836a35d872cf2c77a47b` |

This attempt leaves the ORX node unanswered and eligible for repair under its existing frozen command/source. Preserve this failure and use a new attempt number for any subsequent run.
