# E007 — bounded event-time correctness prototype

Planning alignment: XP004. This additive experiment continues the campaign under the user's instruction to proceed past pending review gates. E007 is an experiment identity and does not indicate that XP001–XP003 passed.

The experiment adds a small event-time accumulator under `src/dce_foundation/representation_v2/temporal.py` and checks it against an independently written offline replay oracle on deterministic synthetic counter events. It covers bounded reordering, one missing value, one counter reset, an out-of-order event beyond the lateness bound, masks, and window boundaries. It is not integrated into the DCE application or delivered R0 system.
