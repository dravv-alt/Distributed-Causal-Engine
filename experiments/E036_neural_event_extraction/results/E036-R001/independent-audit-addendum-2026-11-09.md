# E036-R001 split-overlap audit addendum

Date: 2026-11-09. This addendum records a read-only audit of the existing run. It does not alter the original protocol, predictions, metrics, or decision.

## Finding

The protocol describes 150 separately generated held-out messages. The generator uses the same 12 phrase templates for training and test, changing only `worker`, `attempt`, and other provenance fields. Since inference vectorizes the `text` field, test messages are not template-disjoint from training.

An exact-text comparison found:

- 114 of 150 test rows (76%) have text that occurs in the training set.
- Those rows contain 45 unique exact text strings shared between train and test.
- The overlap contains 38 test rows from each of the three classes.
- No duplicate text mapped to a conflicting class label.

The test labels remained separate from the inference script. This is train/test content overlap, not evidence that evaluator labels were loaded during inference.

## Recomputed result and provenance

From the existing predictions, test labels, and test inputs, a read-only recomputation confirmed 150/150 accuracy, 1.00 macro F1, 0.84 keyword-baseline accuracy, schema compliance, and 150/150 source IDs retained. These values reproduce the stored metrics but do not support a clean held-out-generalization claim because of template overlap and repeated generated patterns.

| Artifact | SHA-256 |
|---|---|
| `fixtures/train.json` | `82dd55831267464bc1f4ea47322fae13ae5cb7afe282addd9618b67befdbfc07` |
| `fixtures/test_inputs.json` | `6c1604c196d26eb062bd2c92d79313f3e5103bf395521771b34585f4354f43fa` |
| `evaluator/train_labels.json` | `b0ac63e1efe66c4b3bd86585116bb5e066cfc534911529bd68954a7f938910bd` |
| `evaluator/test_labels.json` | `3125c1a3eaeb74b3f416becaf935a8269d5edcd0c2d733478d207ca7cba685d3` |
| `results/E036-R001/predictions.json` | `834e1d8d3dadb7d491299626439b33b6ffe520999e2bcbf5c47f29862327e5b3` |

## Scope and next review

Treat the reported synthetic score as a template-pipeline result. Real-data event extraction accuracy remains UNKNOWN, and XP033 is not established as a held-out evaluation. A corrected follow-up would need disjoint generation templates or source groups fixed before training, then a new non-overwriting run and independent audit. XP034 depends on XP033; this finding should be reviewed before claiming that dependency is satisfied. Unrelated eligible campaign work can continue.
