"""Symbolic knowledge: SLO facts, observed degradation onsets, dependency/timing rules.

Cause timestamps are always OBSERVED onsets (never current_time minus a constant).
Every derived fact carries provenance (rule, rule version, input fact ids).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field

import numpy as np

from .schema import FEATURE_INDEX
from .topology import Topology

RULE_VERSION = "dce.rules.v1"


@dataclass(frozen=True)
class RuleConfig:
    rule_version: str = RULE_VERSION
    min_sustain: int = 3          # consecutive observed breaching steps required
    min_lag_s: float = 1.0        # cause must precede effect by at least this
    max_hop_lag_s: float = 6.0    # per-hop propagation bound (configuration, not a universal constant)
    max_hops: int = 4
    enforce_timing: bool = True


class SloConfig:
    """Upper-bound SLO thresholds per service/metric, calibrated from a baseline segment (config, not truth)."""

    def __init__(self, features: tuple, thresholds: np.ndarray):
        self.features = tuple(features)  # monitored feature names
        self.thresholds = thresholds  # (S,M)

    @staticmethod
    def from_baseline(values, mask, monitored=("latency_ms", "error_rate"), z: float = 6.0) -> "SloConfig":
        idx = [FEATURE_INDEX[f] for f in monitored]
        v = np.where(mask[..., idx], values[..., idx], np.nan)
        med = np.nanmedian(v, axis=0)
        mad = np.nanmedian(np.abs(v - med), axis=0) * 1.4826
        return SloConfig(monitored, med + z * np.maximum(mad, 1e-3 * np.abs(med) + 1e-6))

    def disabled(self) -> "SloConfig":
        return SloConfig(self.features, np.full_like(self.thresholds, np.inf))

    def to_dict(self) -> dict:
        return {"features": list(self.features), "thresholds": self.thresholds.tolist()}

    @staticmethod
    def from_dict(d: dict) -> "SloConfig":
        return SloConfig(tuple(d["features"]), np.array(d["thresholds"]))


@dataclass
class Fact:
    kind: str
    args: dict
    rule: str
    rule_version: str
    inputs: tuple = ()
    id: str = ""

    def __post_init__(self):
        if not self.id:
            h = hashlib.sha1(json.dumps([self.kind, self.args, self.rule, list(self.inputs)], sort_keys=True, default=str).encode())
            self.id = h.hexdigest()[:10]

    def to_dict(self) -> dict:
        return {"id": self.id, "kind": self.kind, "args": self.args, "rule": self.rule,
                "rule_version": self.rule_version, "inputs": list(self.inputs)}


@dataclass
class Onset:
    time: float
    uncertainty: float
    source: str  # 'slo' | 'neural'
    fact_id: str
    severity: float = 0.0


def detect_slo(raw, mask, times, slo: SloConfig, cfg: RuleConfig, services):
    """raw (T,S,F) -> (onsets: service->Onset, facts, observed_services)."""
    idx = [FEATURE_INDEX[f] for f in slo.features]
    dt = float(np.median(np.diff(times))) if len(times) > 1 else 1.0
    onsets, facts, observed = {}, [], set()
    for si, svc in enumerate(services):
        obs = mask[:, si, 0]
        if obs.any():
            observed.add(svc)
        ratio = raw[:, si, :][:, idx] / slo.thresholds[si]  # (T,M)
        breach = obs & (ratio > 1.0).any(axis=1)
        run, start, last_obs_before = 0, None, None
        for t in range(len(times)):
            if not obs[t]:
                continue
            if breach[t]:
                run += 1
                if run == 1:
                    start = t
                if run >= cfg.min_sustain:
                    prev = np.nonzero(obs[:start])[0]
                    unc = dt if len(prev) == 0 or prev[-1] == start - 1 else float(times[start] - times[prev[-1]])
                    sev = float(ratio[start:t + 1].max())
                    f = Fact("slo_breach", {"service": svc, "metrics": list(slo.features), "severity": round(sev, 3),
                                            "interval": [int(times[start]), int(times[t])]},
                             "slo_sustained_breach", cfg.rule_version)
                    o = Fact("degradation_onset", {"service": svc, "time": int(times[start]), "uncertainty_s": unc,
                                                   "source": "slo"}, "onset_from_first_breach", cfg.rule_version, (f.id,))
                    facts += [f, o]
                    onsets[svc] = Onset(float(times[start]), unc, "slo", o.id, sev)
                    break
            else:
                run = 0
    return onsets, facts, observed


@dataclass
class PairEvidence:
    effect: str
    cause: str
    path: tuple
    dt: float
    fit: float


@dataclass
class Explanation:
    candidate: str
    explained: dict = field(default_factory=dict)       # effect service -> PairEvidence (includes itself)
    contradicted: list = field(default_factory=list)    # PairEvidence rejected for healthy intermediates


def explain(onsets: dict, topology: Topology, healthy: set, cfg: RuleConfig) -> dict:
    """For each candidate c: which anomalous services does c validly explain?

    c explains a iff a depends (transitively, <= max_hops) on c, c's observed onset precedes a's by
    [min_lag, hops*max_hop_lag], and at least one dependency path has no intermediate observed healthy.
    """
    out = {}
    for c, oc in onsets.items():
        ex = Explanation(c, {c: PairEvidence(c, c, (c,), 0.0, 1.0)})
        for a, oa in onsets.items():
            if a == c:
                continue
            paths = topology.dependency_paths(a, c, cfg.max_hops)
            if not paths:
                continue
            valid = [q for q in paths if not any(n in healthy for n in q[1:-1])]
            path = valid[0] if valid else paths[0]   # explanation holds if ANY path has no healthy intermediate
            hops, dt = len(path) - 1, oa.time - oc.time
            if cfg.enforce_timing and not (cfg.min_lag_s <= dt <= hops * cfg.max_hop_lag_s):
                continue
            fit = 1.0 if (not cfg.enforce_timing or dt <= hops * cfg.max_hop_lag_s / 2) else 0.5
            pe = PairEvidence(a, c, tuple(path), dt, fit)
            (ex.explained.__setitem__(a, pe) if valid else ex.contradicted.append(pe))
        out[c] = ex
    return out
