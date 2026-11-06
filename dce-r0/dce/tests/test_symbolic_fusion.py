import numpy as np

from dce.fusion import FusionConfig, NeuralWindow, fuse
from dce.symbolic import RuleConfig, detect_slo
from dce.topology import Topology
from conftest import make_window, slo_for

R, F = RuleConfig(), FusionConfig()


def run(topo, breach, neural=None, **kw):
    raw, mask, times = make_window(topo, breach, **kw)
    return fuse(raw, mask, times, topo, slo_for(topo), R, F, neural)


def nw(topo, scores):
    s = np.array([scores.get(x, 0.0) for x in topo.services])
    return NeuralWindow(s, np.where(s > 0.5, 3, -1), "m1")


def test_cascade_isolates_true_root_using_observed_onsets(topo):
    d = run(topo, {"user-db": 5, "auth-svc": 7, "lb-1": 9})
    assert d.claim == "causal_hypothesis" and d.root_sets[0]["services"] == ["user-db"]
    assert d.candidates[0].service == "user-db"
    on = {f.args["service"]: f.args["time"] for f in d.facts if f.kind == "degradation_onset"}
    assert on == {"user-db": 5, "auth-svc": 7, "lb-1": 9}       # onsets are observed, not invented
    assert d.confidence_status == "uncalibrated" and d.degraded and d.processing_mode == "symbolic_only"
    assert all(f.rule_version for f in d.facts)                  # provenance on every derived fact


def test_concurrent_unrelated_faults_yield_root_set(topo):
    d = run(topo, {"user-db": 5, "rec-engine": 5})
    assert d.root_sets[0]["services"] == ["rec-engine", "user-db"]


def test_simultaneous_onsets_do_not_explain_each_other(topo):
    d = run(topo, {"user-db": 5, "auth-svc": 5})
    assert d.root_sets[0]["services"] == ["auth-svc", "user-db"]


def test_effect_before_cause_is_impossible(topo):
    d = run(topo, {"user-db": 12, "auth-svc": 5})   # caller degraded first -> user-db cannot explain it
    assert "auth-svc" in d.root_sets[0]["services"]


def test_healthy_intermediate_contradicts_propagation(topo):
    d = run(topo, {"user-db": 5, "lb-1": 9})        # auth-svc/api-svc observed healthy between them
    assert d.root_sets[0]["services"] == ["lb-1", "user-db"]
    assert any(c.contradicting for c in d.candidates if c.service == "user-db")


def test_cycle_terminates_and_respects_order():
    t = Topology.create(["a", "b", "c"], [("a", "b"), ("b", "a"), ("b", "c")])
    d = run(t, {"a": 5, "b": 8})
    assert d.root_sets[0]["services"] == ["a"]


def test_missing_data_widens_uncertainty_not_crash(topo):
    gap = [("user-db", 4, 12)]  # telemetry gap spans the true onset at step 10
    raw, mask, times = make_window(topo, {"user-db": 10}, missing=gap)
    on, facts, _ = detect_slo(raw, mask, times, slo_for(topo), R, topo.services)
    assert on["user-db"].time == 12 and on["user-db"].uncertainty == 9.0   # first OBSERVED breach; gap is honest
    # with an observed healthy sample right before the onset, the onset is tight
    raw, mask, times = make_window(topo, {"user-db": 10}, missing=[("user-db", 4, 9)])
    on, _, _ = detect_slo(raw, mask, times, slo_for(topo), R, topo.services)
    assert on["user-db"].time == 10 and on["user-db"].uncertainty == 1.0
    assert run(topo, {"user-db": 10}, missing=gap).status == "incident"


def test_neural_only_anomaly_never_makes_causal_claim(topo):
    d = run(topo, {}, neural=nw(topo, {"cache": 0.95}))
    assert d.status == "incident" and d.claim == "anomaly_only"
    assert d.root_sets == [] and d.abstention_reason == "insufficient_structural_support"


def test_no_evidence_no_incident(topo):
    assert run(topo, {}, neural=nw(topo, {})).status == "no_incident"


def test_both_branches_change_the_ranking(topo):
    b = {"user-db": 5, "rec-engine": 5}
    hi_rec = run(topo, b, neural=nw(topo, {"rec-engine": 0.99, "user-db": 0.55}))
    hi_db = run(topo, b, neural=nw(topo, {"rec-engine": 0.55, "user-db": 0.99}))
    assert hi_rec.candidates[0].service == "rec-engine" and hi_db.candidates[0].service == "user-db"
    assert hi_rec.processing_mode == "hybrid" and not hi_rec.degraded
    assert hi_rec.candidates[0].contributions["neural"] > 0 and hi_rec.candidates[0].contributions["symbolic"] > 0
    # symbolic input change also matters: dropping the cascade changes the explanation
    casc = run(topo, {"user-db": 5, "auth-svc": 7}, neural=nw(topo, {"user-db": 0.8, "auth-svc": 0.8}))
    flat = run(topo, {"user-db": 5, "auth-svc": 5}, neural=nw(topo, {"user-db": 0.8, "auth-svc": 0.8}))
    assert casc.root_sets[0]["services"] != flat.root_sets[0]["services"]
