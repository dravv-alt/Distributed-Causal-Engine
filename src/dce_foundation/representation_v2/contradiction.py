"""Small deterministic contradiction-aware ranking pilot.

This module encodes an explicitly supplied evidence mapping. It does not parse
telemetry, infer evidence semantics, or establish real-world causality.
"""

from __future__ import annotations


def _rank(candidates: list[str], support: dict[str, list[str]], contradiction: dict[str, list[str]], use_contradiction: bool) -> dict:
    if len(candidates) != len(set(candidates)) or not candidates:
        raise ValueError("candidates must be non-empty and unique")
    if set(support) != set(candidates) or set(contradiction) != set(candidates):
        raise ValueError("evidence maps must exactly match candidates")
    scores = {}
    for candidate in candidates:
        positive = support[candidate]
        negative = contradiction[candidate]
        if len(positive) != len(set(positive)) or len(negative) != len(set(negative)):
            raise ValueError("duplicate evidence reference")
        if set(positive) & set(negative):
            raise ValueError("same evidence cannot support and contradict one candidate")
        scores[candidate] = len(positive) - (len(negative) if use_contradiction else 0)
    maximum = max(scores.values())
    winners = [candidate for candidate, score in scores.items() if score == maximum]
    selected = winners[0] if maximum > 0 and len(winners) == 1 else None
    return {
        "selected": selected,
        "abstained": selected is None,
        "scores": scores,
        "evidence": {
            candidate: {
                "support": list(support[candidate]),
                "contradiction": list(contradiction[candidate]) if use_contradiction else [],
            }
            for candidate in candidates
        },
        "policy": "contradiction_aware_v1" if use_contradiction else "support_only_v1",
    }


def infer_case(case: dict) -> dict[str, dict]:
    required = {"case_id", "candidates", "support", "contradiction"}
    if set(case) != required:
        raise ValueError("unexpected case fields")
    return {
        "support_only_v1": _rank(case["candidates"], case["support"], case["contradiction"], False),
        "contradiction_aware_v1": _rank(case["candidates"], case["support"], case["contradiction"], True),
    }
