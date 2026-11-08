# E019-R001 run record

- Planning stage: XP016.
- Data: 600 fresh synthetic cases, generated with seed 29016; labels separate from inference.
- Comparison: full four-modality score versus neural+symbolic+temporal with topology removed from its ranking and explanation contract.
- Local CPU scripts only; `orx` is unavailable and no remote compute or network calls were used.
- One independent-audit attempt failed on the null/null comparator for no-explanation cases; the failed attempt is recorded in `independent-audit-attempt-001.md`. The corrected independent audit passed and verified the no-topology scores without using graph data.
- Results: `evaluation.json`; limits: `interpretation.md`.
