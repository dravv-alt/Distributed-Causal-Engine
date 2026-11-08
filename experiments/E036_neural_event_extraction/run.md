# E036-R001 run record

- CPU PyTorch run, seed 36033; 300 generated training messages and 150 held-out generated messages across three event classes.
- Neural bag-of-token classifier: accuracy 1.00, macro F1 1.00. Fixed keyword reference: accuracy 0.84.
- All 150 outputs met the declared schema and retained the supplied source ID.
- Test labels were held in `evaluator/test_labels.json`; inference script did not load them.
- The task templates and vocabulary are synthetic and closely related across train/test. Softmax scores are not calibrated. No real RCAEval event annotations were used; no DCE integration is demonstrated.
- No numeric threshold was approved. Descriptive pilot only; no campaign pass claim.
