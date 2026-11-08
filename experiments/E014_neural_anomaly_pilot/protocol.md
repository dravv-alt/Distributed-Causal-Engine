# E014-R001 protocol — frozen before implementation

**Date:** 2026-11-07 (Asia/Calcutta). **Planning alignment:** XP011 / RQ3. **Scope:** nine selected blind RCAEval cases, one from each dataset/system group, dataset revision `afeacb11bcc94dadfd1c8f483ee4377b2b8b614e`.

## Inference and chronological partition

Inference reads only blind case metric Parquet files. Exclude the `time` column from features; use all remaining numeric columns without assigning semantic meaning. For each case, sort by the existing row order and split rows at fixed proportions: first 35% for fitting, next 15% for threshold calibration, final 50% for scoring. No root-cause labels, fault names, injection times, or schedule fields are read by inference or training.

Missing values are median-imputed from the fit partition, with per-feature missingness indicators appended for the neural input. Values are centered by the fit median, scaled by `1.4826 * MAD` with a fallback scale of 1 for zero MAD, and clipped to [-10, 10]. The statistical baseline uses the same standardized values and scores a row by maximum absolute observed-feature z value.

## Methods

- **Statistical baseline:** max absolute robust z-score; threshold is the 95th percentile of calibration-prefix scores.
- **Neural detector:** PyTorch fully connected autoencoder with input dimension twice the feature count (values plus missingness mask), hidden widths 64 then 16 then 64 (adjust the first hidden width to `min(64, input_dim)`), ReLU activations, Adam, learning rate 0.001, weight decay 0.0001, 40 epochs, full-batch fit. Seed 17, CPU only. Reconstruction mean squared error is the anomaly score; threshold is its calibration-prefix 95th percentile.
- Flags are strict score `>` threshold. All hyperparameters and partitions are fixed before observing labels.

## Evaluator metrics

The evaluator obtains `inject_time`, `normal_timesteps`, and `faulty_timesteps` from the pinned evaluator-only RCAEval index through the existing blind-to-source selection manifests. It maps fault labels to metric rows by `metric.time >= inject_time`; a selected case with injection after its telemetry window is treated as an all-normal control. These labels remain in the evaluator process and are not copied into inference artifacts.

Report point-level precision, recall, F1, AUROC when both classes are present, false-positive rate on normal rows, per-fault-case detection rate, and delay in metric timesteps from the first evaluator-marked faulty row to the first alarm at/after that row. Also report per-case counts. Do not interpret timestep delay as a physical duration.

## Validity boundary

The split is chronological within each selected incident; it is not a held-out-incident split. Cases were selected for schema coverage and differ in metric schema. Feature names/values do not establish units, aggregation, resets, or service semantics. A 95th percentile threshold from a short calibration prefix is unstable. Report descriptive results only; no numeric acceptance threshold is approved. Keep all data local; no network or remote compute.
