"""Offline training: chronological split with embargo; ALL statistics fit on the train segment only."""
from __future__ import annotations

import numpy as np

from .neural import ModelBundle, TemporalScorer
from .schema import FEATURES, SCHEMA_VERSION, UNITS
from .simulator import Dataset
from .symbolic import SloConfig
from .windows import (Normalizer, chronological_segments, detection_labels, make_windows, step_labels)


def train_bundle(ds: Dataset, context: int = 30, horizon: int = 30, receptive: int = 5, seed: int = 0,
                 fractions=(0.6, 0.2, 0.2), stride: int = 5) -> ModelBundle:
    T = len(ds.times)
    services = ds.topology.services
    segs = chronological_segments(T, fractions, embargo=context + horizon)
    (a, b), (va, vb) = segs["train"], segs["val"]
    normalizer = Normalizer.fit(ds.values[a:b], ds.mask[a:b])
    slo = SloConfig.from_baseline(ds.values[a:b], ds.mask[a:b])
    labels = step_labels(ds.events, T, services)
    scorer = TemporalScorer.fit(normalizer.transform(ds.values[a:b], ds.mask[a:b]), ds.mask[a:b],
                                labels[a:b], receptive=receptive, seed=seed)

    # choose the operating threshold on the VALIDATION segment (window-level detection F1)
    win = make_windows(ds.values, ds.mask, ds.times, normalizer, context, stride, va, vb)
    out = scorer.infer(win.norm, win.mask)
    y = detection_labels(labels, win.starts, context).reshape(-1)
    best_f1, best_thr = -1.0, 0.5
    for thr in np.linspace(0.05, 0.995, 60):
        p = (out.anomaly_score.reshape(-1) >= thr)
        tp = float((p & y).sum()); fp = float((p & ~y).sum()); fn = float((~p & y).sum())
        f1 = 2 * tp / max(2 * tp + fp + fn, 1.0)
        if f1 > best_f1:
            best_f1, best_thr = f1, float(thr)
    scorer.step_threshold = best_thr
    manifest = {
        "format": "dce.bundle.v1", "schema_version": SCHEMA_VERSION, "features": list(FEATURES), "units": list(UNITS),
        "services": list(services), "max_services": len(services), "topology_version": ds.topology.version,
        "slo": slo.to_dict(), "neural_threshold": best_thr,
        "split": {"fractions": list(fractions), "embargo": context + horizon, "context": context,
                  "horizon": horizon, "stride": stride},
        "training": {"seed": seed, "receptive": receptive, "val_window_f1": round(best_f1, 4),
                     "train_steps": int(b - a), "dataset_meta": ds.meta},
    }
    return ModelBundle(manifest, scorer, normalizer)
