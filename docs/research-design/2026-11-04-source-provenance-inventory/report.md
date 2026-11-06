# Source-provenance inventory: stopping report

Date: 4 November 2026 (Asia/Calcutta). This is the deterministic next evidence-qualification step authorized by the user. It is additive, read-only and does not change a prior experiment, registry, result, source file or artifact.

## Result

No sampled metric is fully semantically qualified. No documented healthy-control source or independent evaluation population was found. The deterministic decision is therefore **STOP — prerequisites remain NOT ESTABLISHED**.

The [inventory](inventory.json) covers all 18 distinct names frozen by the 8 October sample plan. It records only evidence that supports source presence and timestamp scale. Every other required semantic property remains `UNKNOWN`.

| Candidate group | Names | Supported locally/version-linked facts | Qualification |
|---|---:|---|---|
| Bank app | 3 | Field presence; seconds timestamps | NOT QUALIFIED |
| Bank container | 3 | KPI-name/value layout; seconds timestamps | NOT QUALIFIED |
| Market container | 3 | KPI-name/value layout; seconds timestamps | NOT QUALIFIED |
| Market mesh | 3 | KPI-name/value layout; seconds timestamps | NOT QUALIFIED |
| Telecom app | 3 | Field presence; milliseconds timestamps | NOT QUALIFIED |
| Telecom container | 3 | KPI-name/value layout; milliseconds timestamps | NOT QUALIFIED |

## What this evidence does and does not establish

The pinned OpenRCA schemas establish the recorded column layouts and timestamp scales for the corresponding systems. They do not define the sampled KPI meanings, units, kind, temporality, aggregation, reset behavior, exporter configuration, transformation pipeline or local dataset-version match.

The cAdvisor reference defines `container_cpu_cfs_periods_total`, `container_cpu_cfs_throttled_periods_total` and `container_cpu_cfs_throttled_seconds_total`; the local Market names omit `_total`. There is no evidence that the local files came from cAdvisor, which exporter version was used, or whether a transformation renamed/differenced/aggregated these metrics. Consequently, no cAdvisor definition transfers to a local Market metric.

The archived context is fault-centered. Pre-fault timestamps, unlabeled records, low values, numeric variation, and missing log entries cannot establish health. The retained records also cannot form an independent evaluation split because they were already selected into an inherited fault-centered context. No full raw archive or telemetry payload was read during this inventory.

## Required evidence before a new experiment can be proposed

Obtain, from the source owner or a dataset release that explicitly matches the local archive hashes:

1. Metric dictionary/exporter configuration mapping every proposed local name to meaning, unit, kind, temporality, aggregation and reset behavior.
2. Provenance for any renaming, aggregation or transformation between exporter output and the local CSVs.
3. A health-state policy and a documented, time-bounded normal-control population.
4. A population separated from metric selection and later tuning by time, incident or environment, with an explicit leakage review.

That evidence would still require human review before creating an experiment ID, protocol, detector or evaluation split. E004 remains **REVISE / structural prior only**; E002-R002 remains separately approved as **REVISE**.
