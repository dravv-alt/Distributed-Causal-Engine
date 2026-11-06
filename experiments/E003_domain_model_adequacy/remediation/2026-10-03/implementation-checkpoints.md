# Request alignment checkpoints

The user requested periodic rereading after each major step. The controlling source is the 2026-10-03 Real-World RCA Transition attachment, sections 5–11, 28–31 and 35.

## Model and semantic tooling checkpoint

Implemented separate v2 values, candidate timestamp profiling, source identity preservation, unknown metric registry, explicit workbook-cell/merged-range evidence, bounded disk-backed parent resolution, source-row dispositions and isolated evaluation. No RCA model, causal inference, intervention, planning or automatic successor was introduced. Historical v1 code remains untouched.

## Pre-execution test checkpoint

Initial new-suite result: 24 passed, one failed, one setup error. The failed fixture exposed a classifier defect: a later milliseconds-scale value interpreted under a seconds profile was labelled invalid before testing alternate scales. Fixed before corpus execution to classify it as ambiguous. The setup error was Windows sandbox access to pytest's temporary directory. Both failures are preserved here; neither changes the preregistered gate.

The next step is approved execution of the same tests, then corpus validation under the frozen AM001 configuration. RCAEval remains conditional on all A–H gates passing.
