"""Synchronized event-time windows, train-only normalization, chronological splits.

Windows have shape (N, T, S, F): each service owns its own channel (no replication).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Normalizer:
    """Robust per-service/per-feature stats fit on the TRAIN segment only; travels with the model."""
    median: np.ndarray  # (S,F)
    scale: np.ndarray  # (S,F)

    @staticmethod
    def fit(values: np.ndarray, mask: np.ndarray) -> "Normalizer":
        v = np.where(mask, values, np.nan)
        med = np.nanmedian(v, axis=0)
        mad = np.nanmedian(np.abs(v - med), axis=0) * 1.4826
        scale = np.maximum(mad, 1e-3 * np.abs(med) + 1e-6)
        return Normalizer(med.astype(np.float64), scale.astype(np.float64))

    def transform(self, values: np.ndarray, mask: np.ndarray) -> np.ndarray:
        z = (values - self.median) / self.scale
        z = np.sign(z) * np.log1p(np.abs(z))  # compress fault-scale excursions
        return np.where(mask, z, 0.0).astype(np.float32)

    def to_dict(self) -> dict:
        return {"median": self.median.tolist(), "scale": self.scale.tolist()}

    @staticmethod
    def from_dict(d: dict) -> "Normalizer":
        return Normalizer(np.array(d["median"]), np.array(d["scale"]))


@dataclass
class Windows:
    starts: np.ndarray  # (N,) first step index of each window
    times: np.ndarray  # (N,T) epoch seconds
    raw: np.ndarray  # (N,T,S,F) raw units (rules use these)
    norm: np.ndarray  # (N,T,S,F) normalized (models use these)
    mask: np.ndarray  # (N,T,S,F) observed


def make_windows(values, mask, times, normalizer: Normalizer, context: int, stride: int, lo: int, hi: int) -> Windows:
    seg_v, seg_m, seg_t = values[lo:hi], mask[lo:hi], times[lo:hi]
    if len(seg_v) < context:
        raise ValueError("segment shorter than context")

    def win(a, axis_last_dims):
        v = np.lib.stride_tricks.sliding_window_view(a, context, axis=0)  # (n,...,context)
        v = np.moveaxis(v, -1, 1)[::stride]
        return np.ascontiguousarray(v)

    raw, m, tt = win(seg_v, 0), win(seg_m, 0), win(seg_t, 0)
    n = raw.shape[0]
    starts = lo + np.arange(n) * stride
    return Windows(starts, tt, raw, normalizer.transform(raw, m), m)


def step_labels(events, n_steps: int, services) -> np.ndarray:
    """(T,S) bool: service visibly impacted by some fault at that step."""
    lab = np.zeros((n_steps, len(services)), dtype=bool)
    idx = {s: i for i, s in enumerate(services)}
    for e in events:
        for svc, (a, b) in e.impact.items():
            lab[a:b, idx[svc]] = True
    return lab


def detection_labels(step_lab: np.ndarray, starts: np.ndarray, context: int) -> np.ndarray:
    """(N,S): any impact overlapping the observation window (this is DETECTION, not forecasting)."""
    cs = np.vstack([np.zeros((1, step_lab.shape[1])), np.cumsum(step_lab, axis=0)])
    return (cs[starts + context] - cs[starts]) > 0


def forecast_labels(step_lab: np.ndarray, starts: np.ndarray, context: int, horizon: int) -> np.ndarray:
    """(N,S): impact begins strictly AFTER the window within `horizon`, none inside the window."""
    T = step_lab.shape[0]
    cs = np.vstack([np.zeros((1, step_lab.shape[1])), np.cumsum(step_lab, axis=0)])
    end = starts + context
    fut_end = np.minimum(end + horizon, T)
    inside = (cs[end] - cs[starts]) > 0
    future = (cs[fut_end] - cs[end]) > 0
    return future & ~inside


def chronological_segments(n_steps: int, fractions=(0.6, 0.2, 0.2), embargo: int = 40) -> dict:
    """Train/val/test in time order with an embargo gap (>= context + horizon) between segments."""
    usable = n_steps - 2 * embargo
    a = int(usable * fractions[0])
    b = int(usable * fractions[1])
    train = (0, a)
    val = (a + embargo, a + embargo + b)
    test = (val[1] + embargo, n_steps)
    return {"train": train, "val": val, "test": test}
