"""Evidence-linked candidate ranking prototype for local RCA research.

This module combines explicit neural anomaly scores, event-time onset, and
observed call topology. It returns a ranking aid, not a calibrated probability
or a causal conclusion. Every contribution retains its source evidence IDs.
"""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
import math
from typing import Iterable, Mapping

from .representation_v2.model import Dependency, Relation


@dataclass(frozen=True)
class EvidenceSignal:
    evidence_id: str
    resource_id: str
    kind: str
    event_ns: int | None = None
    score: float | None = None


def _average_ranks(values: Mapping[str, float], higher_is_better: bool = True) -> dict[str, float]:
    """Map ordinal ranks to [0, 1], assigning tied values their mean rank."""
    if not values:
        return {}
    ordered = sorted(values, key=lambda name: ((-values[name]) if higher_is_better else values[name], name))
    n = len(ordered)
    result: dict[str, float] = {}
    i = 0
    while i < n:
        j = i + 1
        while j < n and values[ordered[j]] == values[ordered[i]]:
            j += 1
        # One-based rank; best maps to 1, worst maps to 0.
        mean_rank = ((i + 1) + j) / 2
        normalized = 1.0 if n == 1 else (n - mean_rank) / (n - 1)
        for name in ordered[i:j]:
            result[name] = normalized
        i = j
    return result


def rank_candidates(
    candidates: Iterable[str],
    dependencies: Iterable[Dependency],
    signals: Iterable[EvidenceSignal],
    topology_covered_resources: Iterable[str] | None = None,
) -> dict:
    """Rank candidate resources from independent evidence components.

    Supported signal kinds are ``neural_anomaly`` and ``symptom``. Neural
    scores must be finite values in [0, 1]; they are ranked within the case,
    so their magnitude is not interpreted as calibrated confidence. Symptom
    events contribute only when their event time is known. Edges are used only
    when their relation is CALLS and their epistemic status is OBSERVED. A
    topology coverage declaration must explicitly include every candidate;
    missing edges cannot otherwise be distinguished from missing telemetry.
    """
    names = tuple(candidates)
    if not names or any(not isinstance(name, str) or not name for name in names):
        raise ValueError("candidates must contain non-empty resource IDs")
    if len(names) != len(set(names)):
        raise ValueError("candidate resource IDs must be unique")
    candidate_set = set(names)
    topology_coverage = None if topology_covered_resources is None else set(topology_covered_resources)
    if topology_coverage is not None and not topology_coverage <= candidate_set:
        raise ValueError("topology coverage may reference candidates only")

    signal_rows = tuple(signals)
    evidence_ids = [row.evidence_id for row in signal_rows]
    if any(not value for value in evidence_ids) or len(evidence_ids) != len(set(evidence_ids)):
        raise ValueError("evidence IDs must be non-empty and unique")
    for row in signal_rows:
        if row.resource_id not in candidate_set:
            raise ValueError(f"evidence references non-candidate resource: {row.resource_id}")
        if row.kind not in {"neural_anomaly", "symptom"}:
            raise ValueError(f"unsupported evidence kind: {row.kind}")
        if row.kind == "neural_anomaly":
            if row.score is None or not math.isfinite(row.score) or not 0 <= row.score <= 1:
                raise ValueError("neural anomaly scores must be finite and within [0, 1]")
        elif row.score is not None:
            raise ValueError("symptom signals do not accept a numeric score")

    anomaly_rows: dict[str, list[EvidenceSignal]] = defaultdict(list)
    symptom_rows: dict[str, list[EvidenceSignal]] = defaultdict(list)
    for row in signal_rows:
        (anomaly_rows if row.kind == "neural_anomaly" else symptom_rows)[row.resource_id].append(row)

    component_ranks: dict[str, dict[str, float]] = {}
    component_evidence: dict[str, dict[str, list[str]]] = {}

    anomaly_values = {
        name: max(row.score for row in rows if row.score is not None)
        for name, rows in anomaly_rows.items()
    }
    if anomaly_values:
        component_ranks["neural_anomaly"] = _average_ranks(anomaly_values)
        component_evidence["neural_anomaly"] = {
            name: sorted(row.evidence_id for row in anomaly_rows[name]) for name in anomaly_values
        }

    rows_by_resource: dict[str, list[EvidenceSignal]] = defaultdict(list)
    for row in signal_rows:
        rows_by_resource[row.resource_id].append(row)
    onset_values = {
        name: min(row.event_ns for row in rows if row.event_ns is not None)
        for name, rows in rows_by_resource.items()
        if any(row.event_ns is not None for row in rows)
    }
    if onset_values:
        component_ranks["earliest_observed_signal"] = _average_ranks(onset_values, higher_is_better=False)
        component_evidence["earliest_observed_signal"] = {
            name: sorted(row.evidence_id for row in signal_rows
                         if row.resource_id == name and row.event_ns == onset_values[name])
            for name in onset_values
        }

    # In a caller -> callee graph, an upstream fault can affect its callers
    # through the dependency path in reverse. This component measures observed
    # affected callers only; it does not infer a causal edge.
    reverse: dict[str, set[str]] = defaultdict(set)
    valid_edges: list[Dependency] = []
    for dep in dependencies:
        if (dep.relation_type == Relation.CALLS and dep.epistemic_status == "OBSERVED"
                and dep.source in candidate_set and dep.target in candidate_set and dep.evidence):
            reverse[dep.target].add(dep.source)
            valid_edges.append(dep)

    component_exclusions: dict[str, dict] = {}
    if valid_edges and topology_coverage is not None and candidate_set <= topology_coverage:
        symptomatic = set(anomaly_rows) | set(symptom_rows)
        impact_values: dict[str, float] = {}
        impact_evidence: dict[str, list[str]] = {}
        for name in names:
            visited: set[str] = set()
            pending = list(reverse.get(name, ()))
            while pending:
                caller = pending.pop()
                if caller in visited:
                    continue
                visited.add(caller)
                pending.extend(reverse.get(caller, ()))
            affected = visited & symptomatic
            impact_values[name] = float(len(affected))
            edge_ids = [e.dependency_id for e in valid_edges
                        if e.target in visited | {name} and e.source in visited | {name}]
            signal_refs = [row.evidence_id for resource in affected
                           for row in (list(anomaly_rows.get(resource, ()))
                                       + list(symptom_rows.get(resource, ())))]
            impact_evidence[name] = sorted(set(edge_ids + signal_refs))
        component_ranks["observed_caller_impact"] = _average_ranks(impact_values)
        component_evidence["observed_caller_impact"] = impact_evidence
    elif valid_edges:
        component_exclusions["observed_caller_impact"] = {
            "reason": "topology_coverage_not_declared_for_all_candidates",
            "covered_resource_ids": sorted(topology_coverage or set()),
            "missing_resource_ids": sorted(candidate_set - (topology_coverage or set())),
        }
    elif topology_coverage is not None:
        component_exclusions["observed_caller_impact"] = {
            "reason": "no_eligible_observed_call_edges",
            "covered_resource_ids": sorted(topology_coverage),
        }
    else:
        component_exclusions["observed_caller_impact"] = {
            "reason": "topology_coverage_not_declared",
        }

    active_components = tuple(
        component for component, values in component_ranks.items()
        if set(values) == candidate_set
    )
    excluded_components = dict(component_exclusions)
    excluded_components.update({
        component: {
            "reason": "incomplete_candidate_coverage",
            "missing_resource_ids": sorted(candidate_set - set(values)),
        }
        for component, values in component_ranks.items()
        if set(values) != candidate_set
    })
    if not active_components:
        return {
            "status": "ABSTAIN",
            "reason": "no_complete_comparable_component",
            "score_type": "within_case_ordinal_mean",
            "components_used": [],
            "components_excluded": excluded_components,
            "ranked_candidates": [],
            "causal_claim": False,
        }

    ranked = []
    for name in names:
        contributions = {component: component_ranks[component].get(name, 0.0)
                         for component in active_components}
        available = [component for component in active_components if name in component_ranks[component]]
        score = sum(contributions.values()) / len(active_components)
        ranked.append({
            "resource_id": name,
            "score": score,
            "score_type": "within_case_ordinal_mean",
            "components": contributions,
            "component_evidence_ids": {
                component: component_evidence[component].get(name, [])
                for component in active_components
            },
            "components_with_direct_evidence": available,
        })
    ranked.sort(key=lambda row: (-row["score"], row["resource_id"]))
    top = [row for row in ranked if row["score"] == ranked[0]["score"]]
    status = "CANDIDATE" if len(top) == 1 and ranked[0]["score"] > 0 else "ABSTAIN"
    reason = None if status == "CANDIDATE" else (
        "top_score_tie" if len(top) > 1 else "no_positive_evidence_score"
    )
    return {
        "status": status,
        "reason": reason,
        "score_type": "within_case_ordinal_mean",
        "components_used": list(active_components),
        "components_excluded": excluded_components,
        "ranked_candidates": ranked,
        "causal_claim": False,
    }
