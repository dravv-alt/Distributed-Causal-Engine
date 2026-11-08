# E037-R001 audit amendment — evidence identifier leakage

Date: 2026-11-07. This additive note preserves the original run and does not rewrite its metrics.

Review of `generate.py` shows that test `evidence_ids` are constructed using the generated true root index (`M{root}`, `G{root}`, `T{root}`) and then passed in `test_inputs.json`. The neural prediction itself reads only the nine numeric features, and the computed neural Top-1 and metric-only Top-1 metrics do not use those IDs. However, the verifier output copies all three IDs for any accepted candidate without matching them to the proposed candidate. Therefore the reported `accepted_with_evidence_ids` and `explanation_link_coverage` do **not** establish candidate-specific evidence fidelity and are invalid as explanation-fidelity evidence.

The 99.67% neural versus 100% metric-only result remains a generated-data comparison because labels are absent from the numeric inference features. Its generalization limits remain as stated in the original record. XP034's claim of independent candidate-specific explanation verification is not established by E037-R001. A corrected experiment would need candidate-neutral evidence identifiers and verifier-generated links derived from candidate-specific facts.
