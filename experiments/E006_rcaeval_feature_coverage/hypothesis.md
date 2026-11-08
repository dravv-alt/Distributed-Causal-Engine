# E006 preregistered question and hypothesis

**Question:** Across one label-blind sampled case from each of the nine RCAEval dataset/system groups, how much do metric feature names, missingness, modality availability, and exact metric/log timestamp overlap vary?

**Hypothesis:** Feature inventories and observed modality/time coverage vary across sampled cases, so a fixed feature schema and assumed complete alignment cannot be treated as established by one case.

**Independent variables:** sampled dataset/system group and available telemetry modality.

**Dependent measures:** metric row count; non-time feature count; union/intersection of feature names; per-feature non-null counts and dtypes; missing-cell counts; presence/size of logs and traces; exact integer timestamp overlap for metrics and logs.

**Reference:** original Parquet-derived field catalogs and per-case counts retained in each blind case's `field-audit.json`. The audit recomputes aggregate coverage from those catalogs. No predictive baseline is appropriate for this descriptive data audit.

**Limits:** nine selected cases are not a random sample or complete RCAEval coverage. Column names/numeric values do not establish unit, temporality, aggregation, reset, or causal meaning. Exact timestamp equality is not proof of common units, timezone, or aligned event windows. Trace timestamp fields are not joined in this run.
