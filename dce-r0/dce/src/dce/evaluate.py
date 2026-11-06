"""Evaluation: one-to-one event matching, false alerts counted separately, ablations, paired bootstrap."""
from __future__ import annotations

from dataclasses import replace

import numpy as np

from .fusion import Decision, FusionConfig, NeuralWindow, fuse
from .neural import ModelBundle, NeuralOutput
from .simulator import Dataset
from .symbolic import RuleConfig
from .topology import Topology
from .windows import make_windows

METHODS = ("threshold_only", "neural_only", "symbolic_only", "hybrid",
           "hybrid_no_topology", "hybrid_no_timing", "hybrid_shuffled_neural")
USES_NEURAL = {"neural_only", "hybrid", "hybrid_no_topology", "hybrid_no_timing", "hybrid_shuffled_neural"}


def prepare(ds: Dataset, lo: int, hi: int, bundle: ModelBundle, context: int, stride: int):
    win = make_windows(ds.values, ds.mask, ds.times, bundle.normalizer, context, stride, lo, hi)
    return win, bundle.scorer.infer(win.norm, win.mask)


def decide(ds: Dataset, win, nout: NeuralOutput, bundle: ModelBundle, method: str, seed: int = 0) -> list:
    topo = ds.topology
    if method in ("threshold_only", "hybrid_no_topology"):
        topo = Topology.create(topo.services, [])
    slo = bundle.slo.disabled() if method == "neural_only" else bundle.slo
    rule_cfg = RuleConfig(enforce_timing=(method != "hybrid_no_timing"))
    fcfg = FusionConfig(neural_threshold=bundle.manifest["neural_threshold"])
    score, onset = nout.anomaly_score, nout.onset_step
    if method == "hybrid_shuffled_neural":
        perm = np.random.default_rng(seed).permutation(len(score))
        score, onset = score[perm], onset[perm]
    decs = []
    for i in range(len(win.starts)):
        nw = NeuralWindow(score[i], onset[i], bundle.model_version) if method in USES_NEURAL else None
        decs.append(fuse(win.raw[i], win.mask[i], win.times[i], topo, slo, rule_cfg, fcfg, nw))
    return decs


def incidentize(decs: list, merge_gap: int) -> list:
    incs, cur = [], None
    for i, d in enumerate(decs):
        if d.status != "incident":
            continue
        sc = d.candidates[0].ranking_score if d.candidates else 0.0
        if cur is not None and i - cur["last"] <= merge_gap:
            cur["last"] = i
            if sc > cur["best_score"]:
                cur["best"], cur["best_score"] = i, sc
        else:
            cur = {"first": i, "last": i, "best": i, "best_score": sc}
            incs.append(cur)
    for c in incs:
        c["start_t"] = decs[c["first"]].window["start"]
        c["detected_at"] = decs[c["first"]].window["end"]
        c["end_t"] = decs[c["last"]].window["end"]
        c["decision"] = decs[c["best"]]
    return incs


def _event_span(ds, e, pad):
    last = max([b for _, b in e.impact.values()] + [e.end])
    return int(ds.times[e.onset]), int(ds.times[min(last, len(ds.times) - 1)]) + pad


def match(ds: Dataset, incs: list, lo: int, hi: int, pad: int) -> dict:
    """Greedy one-to-one matching by earliest detection.

    An incident matches an event only if it was RAISED (detected_at) inside the event's span: a detection cannot
    precede its fault. An unmatched incident raised while no fault is active is a false positive; one raised
    inside an already-matched event is a duplicate; one raised inside an out-of-segment event is ignored.
    """
    ev_all = ds.events
    ev_in = [e for e in ev_all if lo <= e.onset < hi]
    spans = {e.event_id: _event_span(ds, e, pad) for e in ev_all}
    inside = lambda e, t: spans[e.event_id][0] <= t <= spans[e.event_id][1]
    matched, used = [], set()
    for inc in sorted(incs, key=lambda x: x["detected_at"]):
        cand = [e for e in ev_in if e.event_id not in used and inside(e, inc["detected_at"])]
        if cand:
            e = min(cand, key=lambda x: x.onset)
            used.add(e.event_id)
            matched.append((inc, e))
    matched_inc = {id(m[0]) for m in matched}
    fp = dup = ignored = 0
    for inc in incs:
        if id(inc) in matched_inc:
            continue
        containing = [e for e in ev_all if inside(e, inc["detected_at"])]
        if not containing:
            fp += 1
        elif any(e.event_id in used for e in containing):
            dup += 1
        else:
            ignored += 1
    return {"matched": matched, "n_events": len(ev_in), "false_positives": fp, "duplicates": dup,
            "ignored_other_segment": ignored, "events": ev_in}


def boot_ci(flags, n: int = 1000, seed: int = 0):
    a = np.asarray(flags, dtype=float)
    if len(a) == 0:
        return None
    idx = np.random.default_rng(seed).integers(0, len(a), (n, len(a)))
    m = a[idx].mean(axis=1)
    return [round(float(np.percentile(m, 2.5)), 3), round(float(np.percentile(m, 97.5)), 3)]


def event_level(ds: Dataset, decs: list, ev_in: list, pad: int) -> dict:
    """Per-event coverage: an event is detected if some flagged window ends inside its span; its diagnosis is the
    best-scoring flagged window inside that span. Needed because overlapping/abutting faults merge into one incident."""
    wend = np.array([d.window["end"] for d in decs])
    flag = np.array([d.status == "incident" for d in decs])
    out = {}
    for e in ev_in:
        s0, s1 = _event_span(ds, e, pad)
        idx = np.nonzero(flag & (wend >= s0) & (wend <= s1))[0]
        if len(idx) == 0:
            out[e.event_id] = None
            continue
        best = decs[max(idx, key=lambda i: ((decs[i].candidates[0].ranking_score if decs[i].candidates else 0.0), -i))]
        ranked = [c.service for c in best.candidates]
        out[e.event_id] = {
            "delay": int(wend[idx[0]] - ds.times[e.onset]),
            "top1": bool(ranked) and ranked[0] in e.roots,
            "top3": any(r in e.roots for r in ranked[:3]),
            "in_root_set": bool(best.root_sets) and e.roots[0] in best.root_sets[0]["services"],
            "causal": best.claim == "causal_hypothesis",
        }
    return out


def score_method(ds, win, decs, lo, hi, context, stride, merge_s: int = 60) -> dict:
    """Incident-level (deduplicated, one-to-one) precision + event-level coverage and root attribution."""
    incs = incidentize(decs, merge_gap=max(1, merge_s // stride))
    m = match(ds, incs, lo, hi, pad=context)
    tp, fp = len(m["matched"]), m["false_positives"]
    ev = event_level(ds, decs, m["events"], pad=context)
    det = {k: v for k, v in ev.items() if v is not None}
    n = m["n_events"]
    delays = [v["delay"] for v in det.values()]
    per_event = {k: int(bool(v and v["top1"])) for k, v in ev.items()}
    causal = [v for v in det.values() if v["causal"]]
    mean = lambda xs: round(float(np.mean(xs)), 3) if len(xs) else None
    return {
        "events": n, "incidents": len(incs), "false_positives": fp, "duplicates": m["duplicates"],
        "ignored_other_segment": m["ignored_other_segment"],
        "incident_precision": round(tp / max(tp + fp, 1), 3), "incident_precision_ci95": boot_ci([1] * tp + [0] * fp),
        "incident_recall_one_to_one": round(tp / max(n, 1), 3),
        "event_recall": round(len(det) / max(n, 1), 3),
        "event_recall_ci95": boot_ci([1] * len(det) + [0] * (n - len(det))),
        "detection_delay_s": {"median": float(np.median(delays)) if delays else None,
                              "p95": float(np.percentile(delays, 95)) if delays else None, "n": len(delays)},
        "top1_all_events": round(sum(per_event.values()) / max(n, 1), 3),
        "top1_ci95_all_events": boot_ci(list(per_event.values())),
        "top3_detected": mean([v["top3"] for v in det.values()]),
        "root_in_set_detected": mean([v["in_root_set"] for v in det.values()]),
        "abstain_rate_detected": round(1 - len(causal) / len(det), 3) if det else None,
        "top1_given_causal_claim": mean([v["top1"] for v in causal]),
        "_per_event_top1": per_event,
    }


def paired_gain(per_event_a: dict, per_event_b: dict, n: int = 2000, seed: int = 0):
    ids = sorted(per_event_a)
    d = np.array([per_event_a[i] - per_event_b[i] for i in ids], dtype=float)
    if len(d) == 0:
        return None
    idx = np.random.default_rng(seed).integers(0, len(d), (n, len(d)))
    m = d[idx].mean(axis=1)
    return {"mean_diff": round(float(d.mean()), 3), "ci95": [round(float(np.percentile(m, 2.5)), 3),
                                                              round(float(np.percentile(m, 97.5)), 3)], "n_events": len(d)}


def evaluate_dataset(ds: Dataset, lo: int, hi: int, bundle: ModelBundle, methods=METHODS, context=30, stride=5, seed=0) -> dict:
    win, nout = prepare(ds, lo, hi, bundle, context, stride)
    res = {m: score_method(ds, win, decide(ds, win, nout, bundle, m, seed), lo, hi, context, stride) for m in methods}
    if "hybrid" in res:
        strong = [m for m in ("symbolic_only", "neural_only", "threshold_only") if m in res]
        if strong:
            best = max(strong, key=lambda m: res[m]["top1_all_events"])
            res["hybrid_vs_strongest_ablation"] = {"ablation": best, **(paired_gain(res["hybrid"]["_per_event_top1"],
                                                                                    res[best]["_per_event_top1"]) or {})}
    for v in res.values():
        if isinstance(v, dict):
            v.pop("_per_event_top1", None)
    return res


def false_alert_rate(ds: Dataset, bundle: ModelBundle, methods=("threshold_only", "neural_only", "symbolic_only", "hybrid"),
                     context=30, stride=5) -> dict:
    """Fault-free workload: every incident is a false alert. Report service-hours so small samples are visible."""
    assert not ds.events, "fault-free dataset must contain no events"
    T = len(ds.times)
    win, nout = prepare(ds, 0, T, bundle, context, stride)
    out = {}
    for m in methods:
        incs = incidentize(decide(ds, win, nout, bundle, m), merge_gap=max(1, 60 // stride))
        days = T / 86400.0
        out[m] = {"false_alerts": len(incs), "per_environment_day": round(len(incs) / days, 2),
                  "service_hours": round(T * len(ds.topology.services) / 3600.0, 1)}
    return out


def format_report(name: str, res: dict) -> str:
    rows = ["| method | events | incident P (FP) | event recall | delay med/p95 s | top1 (all events) [CI95] | top3 | root-in-set | abstain |",
            "|---|---|---|---|---|---|---|---|---|"]
    for m, r in res.items():
        if not isinstance(r, dict) or "incident_precision" not in r:
            continue
        dl = r["detection_delay_s"]
        rows.append(f"| {m} | {r['events']} | {r['incident_precision']} ({r['false_positives']}) | {r['event_recall']} | "
                    f"{dl['median']}/{dl['p95']} | {r['top1_all_events']} {r['top1_ci95_all_events']} | "
                    f"{r['top3_detected']} | {r['root_in_set_detected']} | {r['abstain_rate_detected']} |")
    g = res.get("hybrid_vs_strongest_ablation")
    tail = (f"\nhybrid vs strongest ablation ({g['ablation']}): top-1 diff {g.get('mean_diff')} "
            f"CI95 {g.get('ci95')} over {g.get('n_events')} events") if g else ""
    return f"### {name}\n" + "\n".join(rows) + tail
