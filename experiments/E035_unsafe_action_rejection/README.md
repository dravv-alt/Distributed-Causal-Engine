# E035 / XP032: unsafe-action rejection

This additive run record follows the user's 2026-11-07 instruction to continue past pending review holds. It is an offline synthetic plan-validator challenge only. No service action is executed and no production capability is claimed.

Run: `E035-R001`. Inputs are in `fixtures/proposals.json`; expected violation labels are separately held in `evaluator/labels.json`. Run `python experiments/E035_unsafe_action_rejection/run.py`, then `python experiments/E035_unsafe_action_rejection/audit.py`.

The experiment measures refusal correctness and valid-plan acceptance under three declared constraints. The stage card specifies no numeric acceptance threshold, so results are descriptive and no pass decision is assigned.
