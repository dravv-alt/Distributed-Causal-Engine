# E037-R001 provenance review — 2026-11-08

This additive review preserves the original result and the existing `audit-amendment-2026-11-07.md`.

## Integrity and independent checks

- Recomputed all 15 manifest entries; every listed file exists and matches its recorded size and SHA-256 hash.
- Read the inference and evaluation sources. Neural classification uses only the nine numeric features; test labels are read by the separate evaluator after prediction.
- Independently recomputed held-out counts from predictions, numeric test features, and evaluator labels: neural correct 299/300, metric-only correct 300/300, accepted 300/300, abstained 0/300.
- Independently parsed candidate identity from the generated `M*` evidence ID. One accepted row has the wrong neural candidate while its copied evidence ID still names the true root. This confirms the prior audit amendment's candidate/evidence mismatch finding.
- No separate independent-audit JSON is present; the prior dated audit amendment already records the evidence-ID flaw.

## Result and construction limits

The neural proposal is 0.33 percentage points below the simpler metric-only baseline on these 300 generated cases. The verifier accepted every proposal and did not exercise abstention. The generator gives the true root a strong metric signal and matching topology/time flags; non-root candidates receive weaker signals and mostly absent support. This is a highly separable synthetic distribution.

The generator also encodes the true root index in each test evidence ID. The verifier copies the full ID list for any accepted candidate without checking that the IDs support that candidate. One of 300 accepted neural proposals is wrong and carries an ID encoding the true, different root. Therefore the stored 100% evidence-link coverage is not candidate-specific explanation fidelity.

No real RCAEval event, verified symbolic candidate, causal hypothesis, or calibrated probability was evaluated. This is not evidence of real RCA utility or explanation fidelity.

## Provenance and governance discrepancy

File hashes match, but a frozen Git revision/clean source snapshot at execution is not recorded; that provenance remains unknown. The E037 amendment maps XP034 to this synthetic pilot; it does not resolve the unchanged permanent-register discrepancy or authorize a successor stage.

## Bounded disposition

The run shows a small synthetic classifier pipeline and a verifier that failed to reject unsupported candidates. It did not beat the metric-only reference, did not abstain, and its evidence-link measure is invalidated by the root-encoded IDs. XP034's real candidate-verification utility remains UNKNOWN.
