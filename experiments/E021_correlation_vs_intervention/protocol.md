# E021-R001 protocol — frozen before implementation

Date 2026-11-07 (Asia/Calcutta). Stage XP018. Generate 600 cases: 300 direct-cause and 300 common-cause. Seed 21018. Keep the mechanism label in evaluator-only storage.

## Structural mechanisms

- Direct cause: observational treatment A is randomized; outcome Y = 1.3A + 0.7U + independent noise.
- Common cause: A = U + noise; Y = U + independent noise; no A→Y term.
- Each case has 60 observational rows and 30 matched intervention contexts. For each context, record both potential outcomes under do(A=0) and do(A=1) with the same U; the intervention arm must not inspect the hidden mechanism label.
- Direct-cause intervention equations use a fixed 1.3 effect; common-cause intervention outcomes omit A. Noise scale and exact generator are in the frozen script.

## Compared rules and metrics

- Observational rule: declare a causal link if absolute Pearson correlation between A and Y is at least 0.50.
- Intervention rule: declare a causal link if mean paired `Y(do(A=1))-Y(do(A=0))` is at least 0.50.
- Report sensitivity, specificity, balanced accuracy, false-causal rate among common-cause cases, true-causal rate among direct-cause cases, and Wilson 95% intervals. Use identical cases and no tuning.
- Ground-truth mechanism labels are evaluator-only; intervention assignments/outcomes are legitimate inference evidence.

## Assumptions and limits

The potential outcomes are directly observable only in this simulation by construction; a real intervention observes one treatment state per unit and requires design assumptions. This experiment does not prove causal effects in any real service. No network or external datasets are used.
