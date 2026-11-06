"""Versioned, immutable service dependency graph.

Edge semantics (PRD s6): (A, B) means "A depends on B" (A calls B).
  * To explain a symptom at A, walk A's dependencies toward B.
  * Services potentially impacted by a fault at B are B's reverse dependencies.
Cycles are legal; every traversal uses visited sets.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from functools import cached_property

import networkx as nx
import numpy as np


class TopologyError(ValueError):
    pass


@dataclass(frozen=True)
class Topology:
    services: tuple
    edges: tuple  # ((caller, callee), ...) sorted, unique
    version: str

    def __post_init__(self):
        if len(set(self.services)) != len(self.services):
            raise TopologyError("duplicate service ids")
        known = set(self.services)
        for a, b in self.edges:
            if a not in known or b not in known:
                raise TopologyError(f"edge ({a},{b}) references unknown service")
            if a == b:
                raise TopologyError(f"self-dependency on {a}")

    @staticmethod
    def create(services, edges, version: str | None = None) -> "Topology":
        services = tuple(services)
        edges = tuple(sorted({(a, b) for a, b in edges}))
        digest = hashlib.sha256(json.dumps([services, edges]).encode()).hexdigest()
        return Topology(services, edges, version or f"topo-{digest[:12]}")

    @cached_property
    def graph(self) -> nx.DiGraph:
        g = nx.DiGraph()
        g.add_nodes_from(self.services)
        g.add_edges_from(self.edges)
        return g

    @cached_property
    def _paths(self) -> dict:
        return dict(nx.all_pairs_shortest_path(self.graph))

    @cached_property
    def _pcache(self) -> dict:
        return {}

    def dependency_paths(self, effect: str, cause: str, max_hops: int = 4) -> list:
        """All simple dependency paths effect -> cause with <= max_hops edges, shortest first (cycle-safe)."""
        key = (effect, cause, max_hops)
        if key not in self._pcache:
            self._pcache[key] = [[effect]] if effect == cause else sorted(
                nx.all_simple_paths(self.graph, effect, cause, cutoff=max_hops), key=lambda p: (len(p), p))
        return self._pcache[key]

    def index(self, service: str) -> int:
        return self.services.index(service)

    def dependencies(self, service: str) -> tuple:
        return tuple(sorted(self.graph.successors(service)))

    def dependents(self, service: str) -> tuple:
        return tuple(sorted(self.graph.predecessors(service)))

    def dependency_path(self, effect: str, cause: str):
        """Shortest path effect -> ... -> cause along 'depends on' edges, or None."""
        return self._paths.get(effect, {}).get(cause)

    def potential_impact(self, service: str) -> tuple:
        """Topology-only potential impact: everything that transitively depends on `service`."""
        return tuple(sorted(nx.ancestors(self.graph, service)))

    def cycles(self) -> list:
        return [sorted(c) for c in nx.strongly_connected_components(self.graph) if len(c) > 1]

    def to_dict(self) -> dict:
        return {"version": self.version, "services": list(self.services), "edges": [list(e) for e in self.edges]}

    @staticmethod
    def from_dict(d: dict) -> "Topology":
        return Topology.create(d["services"], [tuple(e) for e in d["edges"]], d.get("version"))


def reference_topology() -> Topology:
    deps = {
        "gateway": ["lb-1", "lb-2"],
        "lb-1": ["auth-svc", "api-svc"],
        "lb-2": ["auth-svc", "api-svc"],
        "auth-svc": ["user-db", "cache"],
        "api-svc": ["rec-engine", "user-db"],
        "rec-engine": ["cache"],
        "user-db": [],
        "cache": [],
    }
    services = list(deps)
    return Topology.create(services, [(a, b) for a, bs in deps.items() for b in bs])


def layered_topology(n_services: int, seed: int, layers: int = 4, fanout: int = 2) -> Topology:
    """Random layered DAG (callers in early layers, leaf datastores last) for held-out topologies."""
    rng = np.random.default_rng(seed)
    names = [f"svc-{i:03d}" for i in range(n_services)]
    layer_of = np.sort(rng.integers(0, layers, n_services))
    layer_of[0], layer_of[-1] = 0, layers - 1
    edges = set()
    for i, a in enumerate(names):
        nxt = [names[j] for j in range(n_services) if layer_of[j] == layer_of[i] + 1]
        if nxt:
            for b in rng.choice(nxt, size=min(fanout, len(nxt)), replace=False):
                edges.add((a, str(b)))
    for j, b in enumerate(names):  # ensure every non-root layer node has a caller
        if layer_of[j] > 0 and not any(e[1] == b for e in edges):
            prev = [names[i] for i in range(n_services) if layer_of[i] == layer_of[j] - 1]
            if prev:
                edges.add((str(rng.choice(prev)), b))
    return Topology.create(names, edges)
