import numpy as np
import pytest

from dce.simulator import Dataset, SimConfig, fgn, simulate
from dce.topology import Topology, TopologyError, layered_topology
from dce.windows import (Normalizer, chronological_segments, detection_labels, forecast_labels,
                         make_windows, step_labels)


# ---- topology (TOP-01, s6 edge semantics) ----
def test_edge_direction_semantics(topo):
    assert topo.dependency_path("auth-svc", "user-db") == ["auth-svc", "user-db"]
    assert topo.dependency_path("user-db", "auth-svc") is None  # a callee does not depend on its caller
    assert set(topo.dependents("user-db")) == {"auth-svc", "api-svc"}
    assert {"gateway", "lb-1", "lb-2", "auth-svc", "api-svc"} == set(topo.potential_impact("user-db"))
    assert topo.potential_impact("gateway") == ()


def test_topology_validation_and_versioning():
    with pytest.raises(TopologyError):
        Topology.create(["a"], [("a", "b")])
    with pytest.raises(TopologyError):
        Topology.create(["a"], [("a", "a")])
    a = Topology.create(["a", "b"], [("a", "b")])
    assert a.version == Topology.create(["a", "b"], [("a", "b")]).version
    assert a.version != Topology.create(["a", "b"], []).version


def test_cycles_are_allowed():
    t = Topology.create(["a", "b", "c"], [("a", "b"), ("b", "c"), ("c", "a")])
    assert t.cycles() == [["a", "b", "c"]]
    assert t.dependency_path("a", "c") == ["a", "b", "c"]


# ---- simulator ----
def test_fgn_is_long_range_dependent():
    x = fgn(50000, 0.75, np.random.default_rng(0))
    y = fgn(50000, 0.5, np.random.default_rng(0))
    assert abs(x.std() - 1) < 0.1
    assert np.corrcoef(x[:-1], x[1:])[0, 1] > 0.3          # 2^(2H-1)-1 ~ 0.41
    assert abs(np.corrcoef(y[:-1], y[1:])[0, 1]) < 0.05


def test_simulator_deterministic_and_cause_precedes_effect(topo):
    a = simulate(topo, SimConfig(duration_s=6000, seed=1))
    b = simulate(topo, SimConfig(duration_s=6000, seed=1))
    c = simulate(topo, SimConfig(duration_s=6000, seed=2))
    assert np.array_equal(a.values, b.values) and not np.array_equal(a.values, c.values)
    assert a.events
    for e in a.events:
        root = e.roots[0]
        for svc, (start, _) in e.impact.items():
            if svc != root:
                assert topo.dependency_path(svc, root) is not None   # only callers are impacted
                assert start > e.impact[root][0]                     # cause strictly precedes effect


def test_dataset_roundtrip_and_tamper(tmp_path, small_ds):
    small_ds.save(tmp_path)
    back = Dataset.load(tmp_path)
    assert np.array_equal(back.values, small_ds.values) and len(back.events) == len(small_ds.events)
    (tmp_path / "telemetry.npz").write_bytes((tmp_path / "telemetry.npz").read_bytes()[:-5] + b"xxxxx")
    with pytest.raises(ValueError):
        Dataset.load(tmp_path)


def test_layered_topology_valid():
    t = layered_topology(20, seed=4)
    assert len(t.services) == 20 and t.edges


# ---- windows (FEA-01) ----
def test_windows_have_distinct_service_channels(small_ds):
    nz = Normalizer.fit(small_ds.values[:4000], small_ds.mask[:4000])
    w = make_windows(small_ds.values, small_ds.mask, small_ds.times, nz, 30, 5, 0, 4000)
    assert w.raw.shape[1:] == (30, 8, 4)
    for s in range(8):  # each channel equals ITS OWN service slice, not a tiled copy
        assert np.array_equal(w.raw[7, :, s, :], small_ds.values[w.starts[7]:w.starts[7] + 30, s, :])
    assert not np.allclose(w.raw[:, :, 0, 0], w.raw[:, :, 1, 0])
    assert (w.starts + 30 <= 4000).all()


def test_chronological_segments_have_embargo():
    s = chronological_segments(20000, (0.6, 0.2, 0.2), embargo=60)
    assert s["train"][1] + 60 <= s["val"][0] and s["val"][1] + 60 <= s["test"][0] and s["test"][1] == 20000


def test_normalizer_uses_train_only(small_ds):
    v, m = small_ds.values.copy(), small_ds.mask
    n1 = Normalizer.fit(v[:5000], m[:5000])
    v[6000:] *= 100.0  # corrupt future data
    n2 = Normalizer.fit(v[:5000], m[:5000])
    assert np.array_equal(n1.median, n2.median) and np.array_equal(n1.scale, n2.scale)


def test_detection_vs_forecast_labels_are_distinct():
    lab = np.zeros((100, 1), dtype=bool)
    lab[50:60] = True
    starts = np.array([0, 15, 35, 45])
    det = detection_labels(lab, starts, 10)[:, 0]
    fc = forecast_labels(lab, starts, 10, horizon=10)[:, 0]
    assert det.tolist() == [False, False, False, True]            # only window overlapping the fault
    assert fc.tolist() == [False, False, True, False]              # strictly-after-window, no overlap
    assert not (det & fc).any()
