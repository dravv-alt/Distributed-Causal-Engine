"""Neural perception: one temporal encoder SHARED across services -> per-step anomaly evidence.

Receptive field of k steps over (features + observed-flag) -> small MLP -> per-service, per-step score.
anomaly_score = max over steps (uncalibrated); onset evidence = first step above step_threshold.
Weights are served by a numpy forward pass and stored as JSON+npz (no pickle, checksum-verified).
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .schema import FeatureSchema
from .topology import Topology
from .windows import Normalizer


class BundleIncompatible(ValueError):
    pass


class BundleIntegrityError(ValueError):
    pass


@dataclass
class NeuralOutput:
    anomaly_score: np.ndarray  # (N,S)
    onset_step: np.ndarray  # (N,S) int, -1 = none
    step_scores: np.ndarray  # (N,T,S)


def _step_features(norm: np.ndarray, mask: np.ndarray, k: int) -> np.ndarray:
    """(N,T,S,F),(N,T,S,F) -> (N,T-k+1,S,k*F+k)"""
    v = np.lib.stride_tricks.sliding_window_view(norm, k, axis=1)  # (N,T-k+1,S,F,k)
    N, Tk, S, F, _ = v.shape
    v = np.moveaxis(v, -1, 3).reshape(N, Tk, S, k * F)
    o = np.lib.stride_tricks.sliding_window_view(mask[..., 0].astype(np.float32), k, axis=1)  # (N,T-k+1,S,k)
    return np.concatenate([v, o], axis=-1)


class TemporalScorer:
    def __init__(self, receptive: int, weights: list, step_threshold: float = 0.5):
        self.receptive = receptive
        self.weights = weights  # [(W,b), ...]
        self.step_threshold = step_threshold

    def _forward(self, x: np.ndarray) -> np.ndarray:
        h = x
        for i, (W, b) in enumerate(self.weights):
            h = h @ W + b
            if i < len(self.weights) - 1:
                h = np.maximum(h, 0.0)
        return 1.0 / (1.0 + np.exp(-h[..., 0]))

    def infer(self, norm: np.ndarray, mask: np.ndarray) -> NeuralOutput:
        k = self.receptive
        N, T, S, _ = norm.shape
        feats = _step_features(norm, mask, k).astype(np.float32)
        sc = self._forward(feats)  # (N,T-k+1,S)
        steps = np.zeros((N, T, S), dtype=np.float32)
        steps[:, k - 1:, :] = sc
        above = steps >= self.step_threshold
        any_ = above.any(axis=1)
        onset = np.where(any_, above.argmax(axis=1), -1)
        return NeuralOutput(steps.max(axis=1), onset, steps)

    @staticmethod
    def fit(norm: np.ndarray, mask: np.ndarray, labels: np.ndarray, receptive: int = 5,
            hidden=(32, 16), seed: int = 0, neg_ratio: float = 6.0, max_iter: int = 40) -> "TemporalScorer":
        from sklearn.neural_network import MLPClassifier  # optional 'train' extra

        k = receptive
        x = _step_features(norm[None], mask[None], k)[0]  # (T-k+1,S,d)
        y = labels[k - 1:]
        x2, y2 = x.reshape(-1, x.shape[-1]), y.reshape(-1)
        rng = np.random.default_rng(seed)
        pos = np.nonzero(y2)[0]
        neg = np.nonzero(~y2)[0]
        n_neg = min(len(neg), int(max(len(pos), 1) * neg_ratio))
        sel = np.concatenate([pos, rng.choice(neg, n_neg, replace=False)])
        clf = MLPClassifier(hidden_layer_sizes=hidden, max_iter=max_iter, batch_size=256,
                            random_state=seed, learning_rate_init=1e-3)
        clf.fit(x2[sel], y2[sel])
        return TemporalScorer(k, list(zip(clf.coefs_, clf.intercepts_)))


@dataclass
class ModelBundle:
    manifest: dict
    scorer: TemporalScorer
    normalizer: Normalizer

    @property
    def model_version(self) -> str:
        return self.manifest["model_version"]

    @property
    def slo(self):
        from .symbolic import SloConfig
        return SloConfig.from_dict(self.manifest["slo"])

    def check_compatible(self, topology: Topology, schema: FeatureSchema) -> None:
        FeatureSchema(**{**{"version": self.manifest["schema_version"]},
                         "features": tuple(self.manifest["features"]),
                         "units": tuple(self.manifest["units"])}).check_compatible(schema)
        if tuple(self.manifest["services"]) != tuple(topology.services):
            raise BundleIncompatible("service mapping differs from the bundle's trained service order; "
                                     "a mapping revision and new baseline are required")
        if len(topology.services) > self.manifest["max_services"]:
            raise BundleIncompatible("service count exceeds bundle capacity")

    def save(self, path) -> None:
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        arrays = {}
        for i, (W, b) in enumerate(self.scorer.weights):
            arrays[f"W{i}"], arrays[f"b{i}"] = W, b
        np.savez(path / "weights.npz", **arrays)
        self.manifest["weights_sha256"] = hashlib.sha256((path / "weights.npz").read_bytes()).hexdigest()
        self.manifest["model_version"] = "tmlp-" + self.manifest["weights_sha256"][:12]
        self.manifest["normalizer"] = self.normalizer.to_dict()
        self.manifest["step_threshold"] = self.scorer.step_threshold
        self.manifest["receptive_field"] = self.scorer.receptive
        self.manifest["n_layers"] = len(self.scorer.weights)
        (path / "manifest.json").write_text(json.dumps(self.manifest, indent=1))

    @staticmethod
    def load(path) -> "ModelBundle":
        path = Path(path)
        manifest = json.loads((path / "manifest.json").read_text())
        wfile = path / "weights.npz"
        if hashlib.sha256(wfile.read_bytes()).hexdigest() != manifest["weights_sha256"]:
            raise BundleIntegrityError("weights checksum mismatch; refusing to load")
        z = np.load(wfile, allow_pickle=False)
        weights = [(z[f"W{i}"], z[f"b{i}"]) for i in range(manifest["n_layers"])]
        return ModelBundle(manifest, TemporalScorer(manifest["receptive_field"], weights, manifest["step_threshold"]),
                           Normalizer.from_dict(manifest["normalizer"]))
