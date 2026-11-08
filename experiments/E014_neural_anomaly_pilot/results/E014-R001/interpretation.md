# E014-R001 interpretation

## Aggregate results

The final scored suffix contains 4,947 rows: 4,603 evaluator-marked faulty rows (93.0%) and 344 normal rows.

| Method | Precision | Recall | F1 | AUROC | False-positive rate | Fault cases detected | Mean delay |
|---|---:|---:|---:|---:|---:|---:|---:|
| Robust max-z baseline | 0.000 | 0.000 | 0.000 | 0.560 | 0.000 | 0/8 | — |
| PyTorch autoencoder | 0.973 | 0.948 | 0.960 | 0.924 | 0.346 | 8/8 | 14.5 timesteps |

The autoencoder produced 4,362 true positives, 119 false positives, and 241 false negatives. Its point-level precision is affected by the 93% fault prevalence in this suffix. The false-positive rate is 34.6%; in the no-fault blind control it alarmed on 17 of 32 scored rows. Thus the high event hit rate coexists with substantial false alarms.

The max-z reference produced no alarms. Its zero false-positive rate therefore comes with zero recall and no detected fault cases. The observed result does not establish why its threshold was uninformative.

Detection delay is measured in metric row steps, not seconds. Point-level metrics aggregate serially correlated rows and are not confidence-qualified.

## Integrity and limits

All nine evaluator label alignments matched the indexed faulty-row counts; the prediction seal matched; the corrected independent audit reproduced aggregate and case metrics. Labels, root-cause names, fault types, and injection times were not supplied to model fitting, calibration, or scoring.

This is a within-case chronological split on one selected case from each of nine groups, not held-out-incident validation. The model was fitted separately per case, so it did not test generalization across unseen services or systems. Metric names and values have unqualified semantics, and the selected sample is not population representative. The first half normal fit/calibration assumption was checked against evaluator labels only after scoring and is not an operational guarantee. Short calibration prefixes and all-NaN features weaken threshold stability. No statistical significance or population claim is supported.

The autoencoder exists only in the experimental runner; it is not integrated into the application. E014 is a descriptive XP011 pilot, not a qualified neural anomaly baseline.
