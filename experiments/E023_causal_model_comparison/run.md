# E023-R001 run record

- Planning stage XP020.
- Generated 600 known-mechanism cases (300 per class) with 100 observational rows per case and 40 matched intervention contexts. Ground-truth mechanisms and intervention references were evaluator-only.
- Compared simple observational OLS with OLS conditioned on measured confounder U. A third output records the structural estimate when U is omitted for assumption sensitivity.
- Local NumPy CPU execution; no DoWhy dependency, network, or remote compute.
- Prediction seal verified; independent audit passed all effect and link metrics.
