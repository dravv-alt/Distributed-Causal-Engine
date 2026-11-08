# E036-R001 interpretation

The neural classifier outperformed the fixed keyword reference on the generated held-out set and preserved the expected output envelope. Because this was synthetic data generated from a small repeated vocabulary, the result mainly confirms that the training, inference, and evaluation pipeline executes.

Real-data event extraction accuracy remains unknown: selected RCAEval log rows expose timestamp, container name, and message but no row-level event labels. Case-level fault labels are not an acceptable substitute for event labels and were not exposed to inference.

Disposition: XP033's requested real evidence accuracy is not established. This run is a synthetic pilot only. Human review and an independent labeled source set are still needed for a real-data claim.
