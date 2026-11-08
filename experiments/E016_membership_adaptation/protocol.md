# E016-R001 protocol — frozen before implementation

**Date:** 2026-11-07 (Asia/Calcutta). **Planning alignment:** XP013 / RQ3. **Scope:** synthetic controlled membership experiment; no RCAEval telemetry or evaluator labels.

## Data and split

- Train 300 independently generated cases with exactly eight services and one designated root per case (generator seed 16013).
- Evaluate 100 held-out cases each at 8, 12, and 20 services (generator seeds 18008, 18012, 18020). The eight-service identities are `svc-00` through `svc-07`; larger cases append new service IDs. A separate 100-case permutation set reverses the node ordering of held-out eight-service cases.
- Test inference JSON contains ordered service IDs, two arbitrary synthetic local signals per service, and directed edges. Root labels are stored in a separate evaluator file. Training labels are separate from training inputs and are used only by the supervised training script.
- Each generated case has one injected synthetic root with direct signal shifts; graph descendants receive weaker shifts. Feature values have no real telemetry semantics.

## Methods

- **Fixed-eight baseline:** MLP on a flattened ordered 8×2 feature array; contract requires exactly the canonical eight IDs in canonical order. It rejects additions, removals, substitutions, and reorderings with a membership-mismatch status; it does not silently reorder inputs.
- **Topology-aware shared challenger:** shared per-service MLP over two local signals, normalized outgoing degree, and mean outgoing-neighbor signal. It scores IDs in supplied order and validates unique IDs and edge endpoints. It has no service-ID-specific parameters and accepts any valid membership size.
- Both models train on the same 300 training scenarios for 60 epochs, Adam learning rate 0.005, seed 16013, CPU. No tuning or test-label access.

## Measures

- Root localization: Top-1, Top-3, mean reciprocal rank, and scenario-level 95% Wilson intervals at each size.
- Fixed-baseline mismatch rejection: reject rate for all 200 12/20-service cases and 100 permuted eight-service cases.
- Challenger adaptation: valid-input acceptance at each size and permutation score invariance; malformed duplicate-ID and dangling-edge rejection.
- All metrics are descriptive synthetic results. No acceptance threshold or population claim is preregistered.

## Safety and provenance

Deterministic local generation/training/inference; random seeds as above. PyTorch CPU only. Test labels stay evaluator-only until prediction hashes are sealed. No network or remote compute. Preserve generated inputs, trained weights, predictions, labels hash, logs, source/configuration hashes, and all failures.
