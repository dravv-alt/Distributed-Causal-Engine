# E014 decision status

E014-R001 completed on nine selected RCAEval cases with blind inference, separate evaluator labels, and a sealed prediction file. The corrected independent audit passed and reproduced the evaluator's metrics and per-case summaries.

**Observed outcome:** the neural autoencoder detected 8/8 fault cases in the scored suffix, with point-level F1 0.960 and AUROC 0.924. The scored suffix was 93.0% fault-positive, its false-positive rate was 34.6%, and the no-fault control alarmed on 17/32 rows. The independent robust max-z baseline made no detections.

**Disposition proposal:** REVISE / descriptive neural signal observed under a within-case split; false alarms, short calibration, unqualified feature semantics, selected-case sampling, and lack of held-out incidents prevent XP011 qualification. No quality or generalization claim is made. Human review remains pending.
