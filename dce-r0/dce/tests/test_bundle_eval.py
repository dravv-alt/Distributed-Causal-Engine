import numpy as np
import pytest

from dce.evaluate import match, score_method
from dce.neural import BundleIncompatible, BundleIntegrityError, ModelBundle
from dce.schema import FeatureSchema, SchemaMismatch
from dce.simulator import Dataset, FaultEvent
from dce.topology import Topology
from dce.train import train_bundle


@pytest.fixture(scope="module")
def bundle(small_ds):
    return train_bundle(small_ds, seed=0)


def test_bundle_roundtrip_and_integrity(bundle, small_ds, tmp_path):
    bundle.save(tmp_path)
    b2 = ModelBundle.load(tmp_path)
    x = bundle.normalizer.transform(small_ds.values[:60][None], small_ds.mask[:60][None])
    m = small_ds.mask[:60][None]
    assert np.allclose(bundle.scorer.infer(x, m).anomaly_score, b2.scorer.infer(x, m).anomaly_score)
    (tmp_path / "weights.npz").write_bytes((tmp_path / "weights.npz").read_bytes() + b"x")
    with pytest.raises(BundleIntegrityError):
        ModelBundle.load(tmp_path)


def test_incompatible_bundle_is_rejected(bundle, small_ds, topo):
    bundle.check_compatible(small_ds.topology, FeatureSchema())
    reordered = Topology.create(list(reversed(topo.services)), topo.edges)
    with pytest.raises(BundleIncompatible):
        bundle.check_compatible(reordered, FeatureSchema())
    with pytest.raises(SchemaMismatch):
        bundle.check_compatible(small_ds.topology, FeatureSchema(units=("s", "ratio", "req/s", "ratio")))
    bigger = Topology.create(list(topo.services) + ["x"], topo.edges)
    with pytest.raises(BundleIncompatible):
        bundle.check_compatible(bigger, FeatureSchema())


def _fake_ds(events, T=2000):
    topo = Topology.create(["a", "b"], [("a", "b")])
    return Dataset(topo, ("latency_ms",), np.arange(T, dtype=np.int64), np.zeros((T, 2, 1), np.float32),
                   np.ones((T, 2, 1), bool), events)


def _inc(start, end):
    return {"start_t": start, "detected_at": start + 5, "end_t": end}


def test_matching_is_one_to_one_and_fp_not_success():
    ev = [FaultEvent(0, "x", ("b",), 100, 160, {"b": (100, 160)}),
          FaultEvent(1, "x", ("b",), 1000, 1060, {"b": (1000, 1060)})]
    ds = _fake_ds(ev)
    incs = [_inc(105, 150), _inc(155, 170),      # second incident = repeat of event 0 -> duplicate, not FP
            _inc(500, 520),                       # overlaps nothing -> false positive
            _inc(1010, 1050)]
    m = match(ds, incs, 0, 2000, pad=30)
    assert len(m["matched"]) == 2 and m["false_positives"] == 1 and m["duplicates"] == 1
    assert len({e.event_id for _, e in m["matched"]}) == 2


def test_overlap_with_event_outside_segment_is_ignored_not_fp():
    ev = [FaultEvent(0, "x", ("b",), 100, 160, {"b": (100, 160)})]
    m = match(_fake_ds(ev), [_inc(120, 150)], lo=1000, hi=2000, pad=30)
    assert m["false_positives"] == 0 and m["ignored_other_segment"] == 1 and m["n_events"] == 0


def test_end_to_end_smoke(bundle, small_ds):
    from dce.evaluate import evaluate_dataset
    from dce.windows import chronological_segments
    sp = bundle.manifest["split"]
    lo, hi = chronological_segments(len(small_ds.times), tuple(sp["fractions"]), sp["embargo"])["test"]
    res = evaluate_dataset(small_ds, lo, hi, bundle, methods=("symbolic_only", "hybrid"))
    for m in ("symbolic_only", "hybrid"):
        assert 0 <= res[m]["incident_precision"] <= 1 and 0 <= res[m]["event_recall"] <= 1


def test_persistent_alarm_raised_before_fault_is_false_positive_not_detection():
    ev = [FaultEvent(0, "x", ("b",), 1000, 1060, {"b": (1000, 1060)})]
    inc = {"start_t": 200, "detected_at": 205, "end_t": 1100}   # alarm active long before the fault
    m = match(_fake_ds(ev), [inc], 0, 2000, pad=30)
    assert len(m["matched"]) == 0 and m["false_positives"] == 1


def test_abutting_faults_merged_into_one_incident_are_both_covered_at_event_level():
    from dce.evaluate import event_level
    from dce.fusion import Candidate, Decision
    ev = [FaultEvent(0, "x", ("b",), 100, 140, {"b": (100, 140)}), FaultEvent(1, "x", ("a",), 150, 190, {"a": (150, 190)})]
    ds = _fake_ds(ev)
    def dec(t, svc):
        c = Candidate(svc, 0.9, {}, (svc,), (), (), True, None)
        return Decision("incident", "causal_hypothesis", "symbolic_only", [svc], [c],
                        [{"services": [svc], "ranking_score": 0.9, "unexplained": []}], None, False, True, [], {},
                        {"start": t - 29, "end": t})
    decs = [dec(120, "b"), dec(170, "a")]       # one merged incident, two diagnoses
    res = event_level(ds, decs, ev, pad=30)
    assert res[0]["top1"] and res[1]["top1"] and res[0]["in_root_set"] and res[1]["in_root_set"]
