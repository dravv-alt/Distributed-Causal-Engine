"""Evidence fusion and abstention.

Candidate generation = union(neural detections, SLO breaches). Ranking is transparent and configurable:
  score = w_neural*neural + w_cov*coverage + w_timing*timing - w_contra*contradiction
(when the neural branch is unavailable the symbolic part is renormalized => 'symbolic_only', degraded).
A neural-only anomaly with no structural support opens an anomaly incident but NEVER a causal claim.
Confidence is not calibrated: we return ranking_score and confidence_status='uncalibrated'.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

import numpy as np

from .symbolic import Fact, Onset, RuleConfig, SloConfig, detect_slo, explain
from .topology import Topology


@dataclass(frozen=True)
class FusionConfig:
    neural_threshold: float = 0.5
    w_neural: float = 0.35
    w_coverage: float = 0.40
    w_timing: float = 0.25
    w_contradiction: float = 0.30
    ambiguity_margin: float = 0.03
    max_root_sets: int = 3
    top_k: int = 5


@dataclass
class NeuralWindow:
    anomaly_score: np.ndarray  # (S,)
    onset_step: np.ndarray  # (S,)
    model_version: str = "unversioned"


@dataclass
class Candidate:
    service: str
    ranking_score: float
    contributions: dict
    explained: tuple
    supporting: tuple
    contradicting: tuple
    structural_support: bool
    neural_score: Optional[float]
    severity: float = 0.0

    def to_dict(self) -> dict:
        return {"service": self.service, "ranking_score": round(self.ranking_score, 4),
                "contributions": {k: round(v, 4) for k, v in self.contributions.items()},
                "explained": list(self.explained), "supporting_facts": list(self.supporting),
                "contradicting_facts": list(self.contradicting), "structural_support": self.structural_support,
                "neural_score": None if self.neural_score is None else round(float(self.neural_score), 4)}


@dataclass
class Decision:
    status: str  # no_incident | incident
    claim: str  # none | anomaly_only | causal_hypothesis
    processing_mode: str  # hybrid | symbolic_only | neural_only
    detected: list
    candidates: list
    root_sets: list
    abstention_reason: Optional[str]
    ambiguous: bool
    degraded: bool
    unexplained: list
    versions: dict
    window: dict
    facts: list = field(default_factory=list)
    confidence_status: str = "uncalibrated"

    def to_dict(self) -> dict:
        return {"status": self.status, "claim": self.claim, "processing_mode": self.processing_mode,
                "detected": self.detected, "candidates": [c.to_dict() for c in self.candidates],
                "root_sets": self.root_sets, "abstention_reason": self.abstention_reason,
                "ambiguous": self.ambiguous, "degraded": self.degraded, "unexplained": self.unexplained,
                "confidence_status": self.confidence_status, "versions": self.versions,
                "window": self.window, "facts": [f.to_dict() for f in self.facts]}


def _greedy(first, ranked, detected, explained_of):
    uncovered, picked = set(detected), []
    if first is not None:
        picked.append(first)
        uncovered -= set(explained_of[first])
    for c in ranked:
        if not uncovered:
            break
        if c.service in picked or not c.structural_support:
            continue
        gain = uncovered & set(explained_of[c.service])
        if gain:
            picked.append(c.service)
            uncovered -= gain
    return picked, uncovered


def fuse(raw, mask, times, topology: Topology, slo: SloConfig, rule_cfg: RuleConfig, fusion_cfg: FusionConfig,
         neural: Optional[NeuralWindow]) -> Decision:
    services = topology.services
    mode = "symbolic_only" if neural is None else "hybrid"
    versions = {"topology": topology.version, "rules": rule_cfg.rule_version,
                "model": None if neural is None else neural.model_version}
    window = {"start": int(times[0]), "end": int(times[-1])}

    slo_onsets, facts, observed = detect_slo(raw, mask, times, slo, rule_cfg, services)
    nscore = {}
    if neural is not None:
        for i, s in enumerate(services):
            nscore[s] = float(neural.anomaly_score[i])
    n_flag = {s for s, v in nscore.items() if v >= fusion_cfg.neural_threshold}
    detected = sorted(set(slo_onsets) | n_flag)
    if not detected:
        return Decision("no_incident", "none", mode, [], [], [], None, False, neural is None, [], versions, window)

    onsets = dict(slo_onsets)
    for s in n_flag - set(slo_onsets):
        k = int(neural.onset_step[services.index(s)])
        if k >= 0:
            dt = float(np.median(np.diff(times))) if len(times) > 1 else 1.0
            f = Fact("degradation_onset", {"service": s, "time": int(times[k]), "uncertainty_s": dt, "source": "neural"},
                     "onset_from_neural_step_scores", rule_cfg.rule_version)
            facts.append(f)
            onsets[s] = Onset(float(times[k]), dt, "neural", f.id)
    healthy = observed - set(detected)
    expl = explain(onsets, topology, healthy, rule_cfg)

    cands = []
    nd = len(detected)
    for c in detected:
        e = expl.get(c)
        ns = nscore.get(c) if neural is not None else None
        if e is not None:
            others = [pe for a, pe in e.explained.items() if a != c]
            coverage = len(e.explained) / nd
            timing = float(np.mean([pe.fit for pe in others])) if others else 0.5
            contra = min(1.0, len(e.contradicted) / max(1, nd - 1))
            for pe in others:
                facts.append(Fact("explains", {"cause": c, "effect": pe.effect, "path": list(pe.path), "dt_s": pe.dt},
                                  "dependency_path_with_temporal_order", rule_cfg.rule_version,
                                  (onsets[c].fact_id, onsets[pe.effect].fact_id)))
        else:
            coverage, timing, contra, others = 1.0 / nd, 0.0, 0.0, []
        structural = (c in slo_onsets) or bool(others)
        sym = fusion_cfg.w_coverage * coverage + fusion_cfg.w_timing * timing - fusion_cfg.w_contradiction * contra
        if neural is None:
            score = sym / (fusion_cfg.w_coverage + fusion_cfg.w_timing)
            contrib = {"neural": 0.0, "symbolic": score}
        else:
            contrib = {"neural": fusion_cfg.w_neural * ns, "symbolic": sym}
            score = contrib["neural"] + sym
        sup = tuple(sorted({onsets[c].fact_id} | {onsets[pe.effect].fact_id for pe in others})) if c in onsets else ()
        con = tuple(f"healthy:{n}" for pe in (e.contradicted if e else []) for n in pe.path[1:-1] if n in healthy)
        cands.append(Candidate(c, float(score), contrib, tuple(sorted(e.explained)) if e else (c,), sup, con,
                               structural, ns, onsets[c].severity if c in onsets else 0.0))
    cands.sort(key=lambda x: (-x.ranking_score, -x.severity, x.service))
    explained_of = {c.service: c.explained for c in cands}

    sets, seen = [], set()
    starts = [None] + [c.service for c in cands[1:fusion_cfg.max_root_sets] if c.structural_support]
    for first in starts:
        picked, unc = _greedy(first, cands, detected, explained_of)
        key = tuple(sorted(picked))
        if picked and key not in seen:
            seen.add(key)
            sc = {c.service: c.ranking_score for c in cands}
            sets.append({"services": sorted(picked), "ranking_score": float(np.mean([sc[p] for p in picked])) * (1 - len(unc) / nd),
                         "unexplained": sorted(unc)})
    sets.sort(key=lambda s: -s["ranking_score"])
    sets = sets[:fusion_cfg.max_root_sets]

    if not sets:
        claim, reason, unexplained, ambiguous = "anomaly_only", "insufficient_structural_support", detected, False
    else:
        claim, reason, unexplained = "causal_hypothesis", None, sets[0]["unexplained"]
        ambiguous = len(sets) > 1 and abs(sets[0]["ranking_score"] - sets[1]["ranking_score"]) < fusion_cfg.ambiguity_margin
    return Decision("incident", claim, mode, detected, cands[:fusion_cfg.top_k], sets, reason, ambiguous,
                    neural is None, unexplained, versions, window, facts)
