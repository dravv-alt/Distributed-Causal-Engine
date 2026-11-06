"""Seeded telemetry simulator with labeled faults and dependency-ordered propagation.

Fault in service r at onset t0 degrades r immediately and r's *callers* (reverse dependencies)
after a cumulative per-hop delay, so cause always precedes effect along the dependency path.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

import numpy as np

from .schema import FEATURES, SCHEMA_VERSION, UNITS
from .topology import Topology


@dataclass(frozen=True)
class SimConfig:
    duration_s: int = 20000
    seed: int = 0
    env_seed: int | None = None   # service baselines; defaults to `seed`. Share it across runs of ONE environment
    hurst: float = 0.75
    mean_gap_s: float = 700.0
    p_concurrent: float = 0.10
    min_duration_s: int = 40
    max_duration_s: int = 120
    fault_types: tuple = ("latency_spike", "saturation", "error_burst")
    missing_rate: float = 0.0
    diurnal_period_s: int = 3600
    diurnal_amp: float = 0.10
    load_scale: float = 1.0
    with_faults: bool = True
    max_hops: int = 3
    start_epoch: int = 1_700_000_000


@dataclass
class FaultEvent:
    event_id: int
    fault_type: str
    roots: tuple
    onset: int
    end: int
    impact: dict  # service -> (start_step, end_step) where fault magnitude is clearly visible


@dataclass
class Dataset:
    topology: Topology
    features: tuple
    times: np.ndarray  # (T,) int64 epoch seconds
    values: np.ndarray  # (T,S,F) float32
    mask: np.ndarray  # (T,S,F) bool, True = observed
    events: list
    meta: dict = field(default_factory=dict)

    def save(self, path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        npz = path / "telemetry.npz"
        np.savez_compressed(npz, times=self.times, values=self.values, mask=self.mask)
        digest = hashlib.sha256(npz.read_bytes()).hexdigest()
        manifest = {
            "schema_version": SCHEMA_VERSION,
            "features": list(self.features),
            "units": list(UNITS),
            "topology": self.topology.to_dict(),
            "events": [
                {**asdict(e), "roots": list(e.roots), "impact": {k: list(v) for k, v in e.impact.items()}}
                for e in self.events
            ],
            "meta": self.meta,
            "telemetry_sha256": digest,
        }
        (path / "manifest.json").write_text(json.dumps(manifest, indent=1))

    @staticmethod
    def load(path) -> "Dataset":
        path = Path(path)
        manifest = json.loads((path / "manifest.json").read_text())
        npz = path / "telemetry.npz"
        if hashlib.sha256(npz.read_bytes()).hexdigest() != manifest["telemetry_sha256"]:
            raise ValueError(f"dataset checksum mismatch: {path}")
        z = np.load(npz)
        events = [
            FaultEvent(e["event_id"], e["fault_type"], tuple(e["roots"]), e["onset"], e["end"],
                       {k: tuple(v) for k, v in e["impact"].items()})
            for e in manifest["events"]
        ]
        return Dataset(Topology.from_dict(manifest["topology"]), tuple(manifest["features"]),
                       z["times"], z["values"], z["mask"], events, manifest["meta"])


def fgn(n: int, hurst: float, rng: np.random.Generator) -> np.ndarray:
    """Fractional Gaussian noise via Davies-Harte (unit variance, long-range dependent for H>0.5)."""
    if n < 4:
        return rng.standard_normal(n)
    k = np.arange(n, dtype=float)
    g = 0.5 * (np.abs(k + 1) ** (2 * hurst) - 2 * np.abs(k) ** (2 * hurst) + np.abs(k - 1) ** (2 * hurst))
    r = np.concatenate([g, g[-2:0:-1]])
    m = len(r)
    lam = np.clip(np.fft.fft(r).real, 0, None)
    half = m // 2
    w = np.zeros(m, dtype=complex)
    w[0] = np.sqrt(lam[0] / m) * rng.standard_normal()
    w[half] = np.sqrt(lam[half] / m) * rng.standard_normal()
    j = np.arange(1, half)
    w[j] = np.sqrt(lam[j] / (2 * m)) * (rng.standard_normal(half - 1) + 1j * rng.standard_normal(half - 1))
    w[m - j] = np.conj(w[j])
    return np.fft.fft(w).real[:n]


def _profile(length: int) -> np.ndarray:
    ramp = np.minimum(1.0, (np.arange(length) + 1) / 3.0)
    return np.concatenate([ramp, [2 / 3, 1 / 3]])


def _propagation(topology: Topology, root: str, max_hops: int, rng) -> dict:
    """service -> (hops, delay_steps). Delay accumulates along the BFS tree => cause precedes effect."""
    out = {root: (0, 0)}
    frontier = [root]
    for hop in range(1, max_hops + 1):
        nxt = []
        for u in frontier:
            for v in topology.dependents(u):
                if v not in out:
                    out[v] = (hop, out[u][1] + int(np.ceil(rng.uniform(1.0, 2.5))))
                    nxt.append(v)
        frontier = nxt
    return out


def simulate(topology: Topology, cfg: SimConfig) -> Dataset:
    env = np.random.default_rng(cfg.seed if cfg.env_seed is None else cfg.env_seed)
    rng = np.random.default_rng(cfg.seed)
    T, S = cfg.duration_s, len(topology.services)
    t = np.arange(T)
    capacity = env.uniform(80, 300, S)          # fixed capacity: more load => higher utilization
    base_lat = env.uniform(15, 80, S)
    base_cpu = env.uniform(0.2, 0.45, S)
    base_rate = capacity * cfg.load_scale
    shared = fgn(T, cfg.hurst, rng)
    load = np.exp(0.12 * shared) * (1 + cfg.diurnal_amp * np.sin(2 * np.pi * t / cfg.diurnal_period_s + rng.uniform(0, 6.28)))
    own = np.stack([fgn(T, cfg.hurst, rng) for _ in range(S)], axis=1)
    rate = base_rate * load[:, None] * np.exp(0.05 * own)
    cpu = np.clip(base_cpu * rate / capacity, 0.01, 0.95)
    lat = base_lat * (1 + 0.05 * cpu / (1 - cpu)) * np.exp(rng.standard_normal((T, S)) * 0.04)
    err = np.clip(0.002 + 0.0008 * np.abs(rng.standard_normal((T, S))), 0, 1)

    events = []
    if cfg.with_faults:
        cur = 150.0
        while True:
            gap = rng.uniform(0, 20) if (events and rng.random() < cfg.p_concurrent) else rng.exponential(cfg.mean_gap_s)
            cur += gap
            onset = int(cur)
            dur = int(rng.integers(cfg.min_duration_s, cfg.max_duration_s + 1))
            if onset + dur + 30 >= T:
                break
            root = topology.services[int(rng.integers(S))]
            ftype = str(rng.choice(cfg.fault_types))
            amp = float(rng.uniform(3.0, 6.0))
            impact = {}
            prof = _profile(dur)
            for svc, (hops, delay) in _propagation(topology, root, cfg.max_hops, rng).items():
                s = topology.index(svc)
                idx = onset + delay + np.arange(len(prof))
                ok = idx < T
                idx, m = idx[ok], (amp * 0.7 ** hops) * prof[ok]
                if ftype == "latency_spike":
                    lat[idx, s] *= 1 + m
                    cpu[idx, s] = np.minimum(0.98, cpu[idx, s] + 0.05 * m)
                elif ftype == "saturation":
                    cpu[idx, s] = cpu[idx, s] + (0.97 - cpu[idx, s]) * np.minimum(1, m / 3)
                    lat[idx, s] *= 1 + 0.7 * m
                else:
                    err[idx, s] += 0.03 * m
                    lat[idx, s] *= 1 + 0.25 * m
                vis = np.nonzero(m >= 1.0)[0]
                if len(vis):
                    impact[svc] = (int(idx[vis[0]]), int(idx[vis[-1]]) + 1)
            events.append(FaultEvent(len(events), ftype, (root,), onset, onset + dur, impact))

    values = np.stack([lat, err, rate, np.clip(cpu, 0, 0.99)], axis=2).astype(np.float32)
    mask = np.ones(values.shape, dtype=bool)
    if cfg.missing_rate > 0:
        n_bursts = int(cfg.missing_rate * T * S / 15)
        for _ in range(n_bursts):
            s, st, ln = int(rng.integers(S)), int(rng.integers(T)), int(rng.integers(5, 30))
            mask[st:st + ln, s, :] = False
        values = np.where(mask, values, 0.0).astype(np.float32)
    meta = {"sim_config": {k: (list(v) if isinstance(v, tuple) else v) for k, v in asdict(cfg).items()}}
    return Dataset(topology, FEATURES, (cfg.start_epoch + t).astype(np.int64), values, mask, events, meta)
