"""Deterministic root-set scoring pilot for explicitly supplied support facts."""

from __future__ import annotations


def rank_roots(candidates: list[str], support: dict[str, list[str]], threshold: int = 2) -> dict:
    if threshold <= 0:
        raise ValueError("threshold must be positive")
    if not candidates or len(candidates) != len(set(candidates)):
        raise ValueError("candidates must be non-empty and unique")
    if set(support) != set(candidates):
        raise ValueError("support map must exactly match candidates")
    scores = {}
    for name in candidates:
        evidence_ids = support[name]
        if len(evidence_ids) != len(set(evidence_ids)):
            raise ValueError("duplicate evidence reference")
        scores[name] = len(evidence_ids)
    maximum = max(scores.values())
    winners = [name for name, score in scores.items() if score == maximum]
    single = [winners[0]] if maximum > 0 and len(winners) == 1 else []
    root_set = sorted(name for name, score in scores.items() if score >= threshold)
    return {
        "single_root_v1": {"selected_roots": single, "scores": scores},
        "root_set_threshold_2_v1": {"selected_roots": root_set, "scores": scores},
    }
