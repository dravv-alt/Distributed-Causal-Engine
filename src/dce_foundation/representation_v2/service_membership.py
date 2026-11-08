"""Experimental fixed and variable-membership neural scorers."""

from __future__ import annotations

import math

import numpy as np
from torch import nn


CANONICAL_EIGHT = tuple(f"svc-{i:02d}" for i in range(8))


class FixedEightModel(nn.Module):
    """Order-sensitive reference model whose contract is exactly eight nodes."""

    def __init__(self):
        super().__init__()
        self.layers = nn.Sequential(nn.Linear(16, 64), nn.ReLU(), nn.Linear(64, 8))

    def forward(self, x):
        if x.ndim != 3 or tuple(x.shape[1:]) != (8, 2):
            raise ValueError("fixed model requires shape (batch, 8, 2)")
        return self.layers(x.reshape(x.shape[0], 16))


class SharedTopologyModel(nn.Module):
    """Shared per-service scorer using local signal and one-hop graph features."""

    def __init__(self):
        super().__init__()
        self.scorer = nn.Sequential(nn.Linear(4, 32), nn.ReLU(), nn.Linear(32, 16), nn.ReLU(), nn.Linear(16, 1))

    def forward(self, x):
        if x.ndim != 3 or x.shape[2] != 4:
            raise ValueError("shared model requires shape (batch, services, 4)")
        return self.scorer(x).squeeze(-1)


def service_features(case: dict) -> tuple[list[str], np.ndarray]:
    if set(case) != {"scenario_id", "nodes", "edges"}:
        raise ValueError("unexpected scenario fields")
    nodes = case["nodes"]
    ids = [node.get("service_id") for node in nodes]
    if not ids or any(not isinstance(value, str) or not value for value in ids) or len(ids) != len(set(ids)):
        raise ValueError("service IDs must be non-empty and unique")
    values = {}
    for node in nodes:
        if set(node) != {"service_id", "signals"} or len(node["signals"]) != 2:
            raise ValueError("each node requires two signals")
        row = [float(v) for v in node["signals"]]
        if not all(math.isfinite(value) for value in row):
            raise ValueError("signals must be finite")
        values[node["service_id"]] = row
    outgoing = {node_id: [] for node_id in ids}
    seen_edges = set()
    for edge in case["edges"]:
        if not isinstance(edge, list) or len(edge) != 2:
            raise ValueError("edges must be source-target pairs")
        source, target = edge
        if source not in outgoing or target not in outgoing:
            raise ValueError("edge endpoint is outside service membership")
        if source == target or (source, target) in seen_edges:
            raise ValueError("self or duplicate edges are invalid")
        seen_edges.add((source, target))
        outgoing[source].append(target)
    denom = max(1, len(ids) - 1)
    features = []
    for node_id in ids:
        neighbors = outgoing[node_id]
        neighbor_mean = sum(values[neighbor][0] for neighbor in neighbors) / len(neighbors) if neighbors else 0.0
        features.append([values[node_id][0], values[node_id][1], len(neighbors) / denom, neighbor_mean])
    return ids, np.asarray(features, dtype=np.float32)
