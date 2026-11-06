# V004 storage amendment

This record preserves the AM002 storage controls. V004 creates a separate `results/V004` directory, verifies archives before writes, imports only verified complete V002 checkpoints, and stops at the existing 6 GiB free-space floor. The Google Drive archive reader is read-only and does not cache, copy, move, modify, or delete the dataset.
