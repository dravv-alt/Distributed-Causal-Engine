# E038-R001 provenance review — 2026-11-08

This additive review preserves the original protocol and result artifacts.

## Integrity and independent audit

- Recomputed all 13 artifact-manifest entries; every listed file exists and matches its recorded size and SHA-256 hash.
- Recomputed all seven hashes in `independent-audit-addendum-2026-11-08.json`; they match the protocol, configuration, fixture, inference source, predictions, metrics, and evaluator labels.
- Read the independent audit source. It recomputes every prediction directly from the frozen three-part rule and checks that inference source does not load evaluator labels. Its PASS is fixture-to-rule consistency, not hypothesis quality.

## Result and construction limits

The stored run reports 100/100 explicitly supported proposals accepted, 100/100 explicitly unsupported proposals rejected, and 100/100 missing-modality proposals abstained. Those outcomes follow directly from the fixture values: supported cases use metric 0.9 with both support flags true; unsupported cases use 0.1 with both false; missing-modality cases use metric 0.9 but a false temporal flag.

The proposals are hand-constructed and all name the same candidate; they are not outputs of the E036 model. Evidence IDs are synthetic strings, with no evidence content or candidate-specific factual audit. The test does not challenge ambiguous, fabricated, conflicting, adversarial, or real evidence, and it does not test DCE integration.

## Provenance and governance discrepancy

The stored manifest and independent-audit hashes are consistent. A frozen Git revision/clean source snapshot at the original run time is not recorded; that provenance remains unknown.

The additive E038 amendment maps XP035 to this synthetic verifier challenge. No approved numeric threshold exists, and this run does not establish neural-hypothesis rejection quality or authorize a production safety claim.

## Bounded disposition

The deterministic verifier matches its deliberately simple fixtures. This is a rule-path sanity check, not evidence that DCE rejects hallucinated real root-cause hypotheses.
