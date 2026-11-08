# E014-R001 protocol deviation 001 — per-case seed offsets

The protocol names seed 17. The runner resets PyTorch's seed to `17 + case_index` for each case in the frozen case order, producing deterministic seeds 17 through 25. This is visible in the preserved runner and does not use labels. The run remains reproducible, but it does not use the single identical seed on every case implied by the protocol text. No rerun or metric change is made; report this as a protocol deviation.
