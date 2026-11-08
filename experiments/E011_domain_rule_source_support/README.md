# E011 — XP008 domain-rule source-support audit

This local exploratory run checks whether the nine already selected, blind RCAEval cases contain literal telemetry fields or log text matching the illustrative XP008 rule predicates (database saturation, pool saturation, and downstream latency). It does not score diagnoses or validate a domain rule. Evaluation labels are never opened.

Planning alignment: XP008. The user explicitly instructed the campaign to continue past pending review gates. This additive registration records the source-data readiness question only; it does not mark XP008 passed or qualify the illustrative rule.

Run from the repository root:

```powershell
python experiments/E011_domain_rule_source_support/scripts/run_audit.py
```

The runner reads only `data/rcaeval/inference/` and `src/dce_foundation/domain.py`, writes aggregate counts and hashes to `results/E011-R001/`, and makes no network calls.
