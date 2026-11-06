# Event-time model

Event time describes measurement occurrence; receipt and processing times describe ingestion and execution.
Use UTC intervals with explicit inclusion rules, source cadence and ordering. Windows align services to a declared event-time grid.

Specify context, stride, watermark/lateness allowance, bounded interpolation, missingness and late-event policy per experiment.
A sample outside lateness policy is rejected or replayed with an explicit reason; it is not silently assigned to a current window.
Keep training/validation/test boundaries and embargo intervals separate from runtime watermarks.

Cold-start detection delay, collection delay, window eligibility delay and processing latency must be reported separately.
A worker owns a coherent analysis scope; lease fencing and checkpoints are required before concurrent live processing.
R0 assumes pre-aligned one-second arrays. Watermarks, live resampling and restart ownership remain planned.
