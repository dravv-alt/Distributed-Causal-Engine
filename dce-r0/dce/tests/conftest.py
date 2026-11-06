import numpy as np
import pytest

from dce.schema import FEATURES
from dce.simulator import SimConfig, simulate
from dce.symbolic import SloConfig
from dce.topology import reference_topology


@pytest.fixture(scope="session")
def topo():
    return reference_topology()


@pytest.fixture(scope="session")
def small_ds(topo):
    return simulate(topo, SimConfig(duration_s=9000, seed=3, mean_gap_s=400))


def make_window(topo, breach: dict, T=30, missing=()):
    """raw (T,S,F) healthy latency=10ms; `breach` maps service -> first breaching step (stays breaching)."""
    S, F = len(topo.services), len(FEATURES)
    raw = np.zeros((T, S, F), dtype=np.float32)
    raw[:, :, 0] = 10.0
    for svc, t0 in breach.items():
        raw[t0:, topo.index(svc), 0] = 100.0
    mask = np.ones((T, S, F), dtype=bool)
    for svc, a, b in missing:
        mask[a:b, topo.index(svc), :] = False
    return raw, mask, np.arange(T, dtype=np.int64)


def slo_for(topo, thr=50.0):
    return SloConfig(("latency_ms",), np.full((len(topo.services), 1), thr))
