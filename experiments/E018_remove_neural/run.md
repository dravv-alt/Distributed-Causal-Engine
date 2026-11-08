# E018-R001 run record

- Planning alignment: XP015, remove neural evidence.
- 600 generated held-out cases, fresh seed 28015; evaluator labels are separate.
- Arms: four-modality full rank fusion versus the same fixed rank fusion without the neural signal. The neural-disabled score vectors were independently reconstructed for all cases from topology, temporal, and symbolic features only; its explanation endpoint selection did not read neural values.
- Local Python/NumPy CPU only. `orx` is unavailable; no managed or remote OpenResearch execution occurred. No script network calls.
- Prediction hash sealed before evaluation. Independent audit passed both arms' reported metrics and the label-separation check.
- Result limitations and interpretation: `results/E018-R001/interpretation.md`.
