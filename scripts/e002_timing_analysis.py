"""Frozen E002-R001 timing/provenance experiment runner.

This is experiment-local analysis code.  It imports the delivered R0 package but
does not alter it.  The same-source policy holds detection and candidate
generation constant and filters only cross-provenance temporal explanations.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np

from dce.evaluate import event_level, incidentize, match, prepare, score_method
from dce.fusion import Candidate, Decision, FusionConfig, NeuralWindow, _greedy
from dce.neural import ModelBundle
from dce.simulator import SimConfig, simulate
from dce.symbolic import Fact, Onset, RuleConfig, detect_slo, explain
from dce.topology import reference_topology
from dce.train import train_bundle


def _fuse_policy(raw, mask, times, topology, slo, rule_cfg, fusion_cfg, neural, policy):
    """R0 fusion with an E002-only timing-evidence policy.

    `mixed_current` is behaviorally equivalent to R0 hybrid. `same_source_only`
    accepts a timing pair only when its cause/effect onsets share `slo` or
    `neural` provenance. `timing_disabled` is the no-temporal-order control.
    """
    services = topology.services
    versions = {"topology": topology.version, "rules": rule_cfg.rule_version,
                "model": neural.model_version}
    window = {"start": int(times[0]), "end": int(times[-1])}
    slo_onsets, facts, observed = detect_slo(raw, mask, times, slo, rule_cfg, services)
    nscore = {s: float(neural.anomaly_score[i]) for i, s in enumerate(services)}
    n_flag = {s for s, value in nscore.items() if value >= fusion_cfg.neural_threshold}
    detected = sorted(set(slo_onsets) | n_flag)
    if not detected:
        return (Decision("no_incident", "none", "hybrid", [], [], [], None, False, False, [], versions, window),
                {"slo_slo": 0, "neural_neural": 0, "cross_source": 0, "used": 0, "used_cross_source": 0})

    onsets = dict(slo_onsets)
    for service in n_flag - set(slo_onsets):
        step = int(neural.onset_step[services.index(service)])
        if step >= 0:
            interval = float(np.median(np.diff(times))) if len(times) > 1 else 1.0
            fact = Fact("degradation_onset", {"service": service, "time": int(times[step]),
                        "uncertainty_s": interval, "source": "neural"},
                        "onset_from_neural_step_scores", rule_cfg.rule_version)
            facts.append(fact)
            onsets[service] = Onset(float(times[step]), interval, "neural", fact.id)
    healthy = observed - set(detected)
    expl = explain(onsets, topology, healthy, rule_cfg)

    candidates, pair_counts = [], {"slo_slo": 0, "neural_neural": 0, "cross_source": 0, "used": 0, "used_cross_source": 0}
    n_detected = len(detected)
    for cause in detected:
        evidence = expl.get(cause)
        neural_score = nscore[cause]
        if evidence is not None:
            potential = [pair for effect, pair in evidence.explained.items() if effect != cause]
            retained = []
            for pair in potential:
                sources = (onsets[cause].source, onsets[pair.effect].source)
                if sources[0] == sources[1]:
                    pair_counts[f"{sources[0]}_{sources[1]}"] += 1
                else:
                    pair_counts["cross_source"] += 1
                if policy != "same_source_only" or sources[0] == sources[1]:
                    retained.append(pair)
            if policy == "timing_disabled":
                retained = potential
            pair_counts["used"] += len(retained)
            pair_counts["used_cross_source"] += sum(onsets[cause].source != onsets[pair.effect].source for pair in retained)
            coverage = (1 + len(retained)) / n_detected
            timing = float(np.mean([pair.fit for pair in retained])) if retained else 0.5
            contradiction = min(1.0, len(evidence.contradicted) / max(1, n_detected - 1))
            explained = {cause: evidence.explained[cause], **{p.effect: p for p in retained}}
            for pair in retained:
                facts.append(Fact("explains", {"cause": cause, "effect": pair.effect, "path": list(pair.path),
                                                "dt_s": pair.dt}, "dependency_path_with_temporal_order",
                                  rule_cfg.rule_version, (onsets[cause].fact_id, onsets[pair.effect].fact_id)))
        else:
            coverage, timing, contradiction, retained, explained = 1.0 / n_detected, 0.0, 0.0, [], {cause: None}
        structural = (cause in slo_onsets) or bool(retained)
        symbolic = fusion_cfg.w_coverage * coverage + fusion_cfg.w_timing * timing - fusion_cfg.w_contradiction * contradiction
        score = fusion_cfg.w_neural * neural_score + symbolic
        supporting = tuple(sorted({onsets[cause].fact_id} | {onsets[p.effect].fact_id for p in retained})) if cause in onsets else ()
        candidates.append(Candidate(cause, float(score), {"neural": fusion_cfg.w_neural * neural_score, "symbolic": symbolic},
                                    tuple(sorted(explained)), supporting, (), structural, neural_score,
                                    onsets[cause].severity if cause in onsets else 0.0))
    candidates.sort(key=lambda c: (-c.ranking_score, -c.severity, c.service))
    explained_of = {candidate.service: candidate.explained for candidate in candidates}
    sets, seen = [], set()
    starts = [None] + [candidate.service for candidate in candidates[1:fusion_cfg.max_root_sets] if candidate.structural_support]
    for first in starts:
        picked, unexplained = _greedy(first, candidates, detected, explained_of)
        key = tuple(sorted(picked))
        if picked and key not in seen:
            seen.add(key)
            scores = {candidate.service: candidate.ranking_score for candidate in candidates}
            sets.append({"services": sorted(picked), "ranking_score": float(np.mean([scores[p] for p in picked])) * (1 - len(unexplained) / n_detected), "unexplained": sorted(unexplained)})
    sets.sort(key=lambda value: -value["ranking_score"])
    sets = sets[:fusion_cfg.max_root_sets]
    if not sets:
        claim, reason, unexplained = "anomaly_only", "insufficient_structural_support", detected
    else:
        claim, reason, unexplained = "causal_hypothesis", None, sets[0]["unexplained"]
    decision = Decision("incident", claim, "hybrid", detected, candidates[:fusion_cfg.top_k], sets, reason, False,
                        False, unexplained, versions, window, facts)
    return decision, pair_counts


def _evaluate(dataset, bundle, policy):
    windows, neural = prepare(dataset, 0, len(dataset.times), bundle, context=bundle.manifest["split"]["context"], stride=bundle.manifest["split"]["stride"])
    cfg = FusionConfig(neural_threshold=bundle.manifest["neural_threshold"])
    rule = RuleConfig(enforce_timing=policy != "timing_disabled")
    decisions, totals = [], {"slo_slo": 0, "neural_neural": 0, "cross_source": 0, "used": 0, "used_cross_source": 0}
    for index in range(len(windows.starts)):
        result = _fuse_policy(dataset.values[windows.starts[index]:windows.starts[index] + windows.raw.shape[1]],
                              windows.mask[index], windows.times[index], dataset.topology, bundle.slo, rule, cfg,
                              NeuralWindow(neural.anomaly_score[index], neural.onset_step[index], bundle.model_version), policy)
        decision, counts = result
        decisions.append(decision)
        for key, value in counts.items():
            totals[key] += value
    context, stride = bundle.manifest["split"]["context"], bundle.manifest["split"]["stride"]
    score = score_method(dataset, windows, decisions, 0, len(dataset.times), context, stride)
    matched = match(dataset, incidentize(decisions, merge_gap=max(1, 60 // stride)), 0, len(dataset.times), context)
    per_event = event_level(dataset, decisions, matched["events"], context)
    return {"metrics": score, "per_event_top1": {str(k): int(bool(v and v["top1"])) for k, v in per_event.items()}, "pair_counts": totals}


def _canonical_sha(value):
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def _bootstrap(diff, seed=909, repetitions=2000):
    values = np.asarray(diff, dtype=float)
    if not len(values):
        return {"mean": None, "ci95": None, "n_events": 0}
    rng = np.random.default_rng(seed)
    sample = values[rng.integers(0, len(values), (repetitions, len(values)))].mean(axis=1)
    return {"mean": round(float(values.mean()), 6), "ci95": [round(float(np.percentile(sample, 2.5)), 6), round(float(np.percentile(sample, 97.5)), 6)], "n_events": int(len(values))}


def _dataset(seed, duration, env_seed, gap=700, concurrent=0.1):
    return simulate(reference_topology(), SimConfig(duration_s=duration, seed=seed, env_seed=env_seed,
                                                     mean_gap_s=gap, p_concurrent=concurrent))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text())
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    generated = {"repeatability": [], "heldout": {}}

    repeat = config["data_generation"]["repeatability"]
    for number in range(1, repeat["repetitions"] + 1):
        train = _dataset(11, 40000, 11)
        repeat_dir = out / f"repeat-{number:03d}"
        train.save(repeat_dir / "train")
        trained = train_bundle(train, seed=config["data_generation"]["model_training_seed"])
        trained.save(repeat_dir / "bundle")
        bundle = ModelBundle.load(repeat_dir / "bundle")
        heldout = _dataset(repeat["heldout_seed"], repeat["duration_s"], repeat["env_seed"], repeat["mean_gap_s"], repeat["p_concurrent"])
        heldout.save(repeat_dir / "heldout")
        result = {name: _evaluate(heldout, bundle, name) for name in config["treatments"]}
        canonical = _canonical_sha(result)
        generated["repeatability"].append({"repeat": number, "canonical_metrics_sha256": canonical, "results": result})

    train = _dataset(11, 40000, 11)
    performance_dir = out / "performance"
    train.save(performance_dir / "train")
    trained = train_bundle(train, seed=config["data_generation"]["model_training_seed"])
    trained.save(performance_dir / "bundle")
    bundle = ModelBundle.load(performance_dir / "bundle")
    all_diffs, aggregate_pairs, aggregate_alerts = [], {name: 0 for name in config["treatments"]}, {name: 0 for name in config["treatments"]}
    aggregate_used_cross = {name: 0 for name in config["treatments"]}
    for seed in config["data_generation"]["heldout"]["seeds"]:
        heldout = _dataset(seed, 30000, 11)
        heldout.save(performance_dir / f"heldout-{seed}")
        result = {name: _evaluate(heldout, bundle, name) for name in config["treatments"]}
        generated["heldout"][str(seed)] = result
        for event_id, consistent in result["same_source_only"]["per_event_top1"].items():
            all_diffs.append(consistent - result["mixed_current"]["per_event_top1"][event_id])
        for name, value in result.items():
            aggregate_pairs[name] += value["pair_counts"]["cross_source"]
            aggregate_used_cross[name] += value["pair_counts"]["used_cross_source"]
            aggregate_alerts[name] += value["metrics"]["false_positives"]
    bootstrap = _bootstrap(all_diffs)
    repeat_hashes = [entry["canonical_metrics_sha256"] for entry in generated["repeatability"]]
    gates = {
        "repeatability": len(set(repeat_hashes)) == 1,
        "treatment_integrity": all(entry["results"]["same_source_only"]["pair_counts"]["used_cross_source"] == 0 for entry in generated["repeatability"]) and aggregate_used_cross["same_source_only"] == 0,
        "superiority": bool(bootstrap["mean"] is not None and bootstrap["mean"] >= 0.05 and bootstrap["ci95"][0] > 0 and aggregate_alerts["same_source_only"] <= aggregate_alerts["mixed_current"])
    }
    # Cross-source candidates are counted before filtering, while used pairs are retained after filtering.
    gates["treatment_integrity"] = all(entry["results"]["same_source_only"]["pair_counts"]["used"] <= entry["results"]["mixed_current"]["pair_counts"]["used"] for entry in generated["repeatability"]) and gates["treatment_integrity"]
    summary = {"configuration_sha256": hashlib.sha256(Path(args.config).read_bytes()).hexdigest(), "repeatability_hashes": repeat_hashes,
               "paired_top1_same_source_minus_mixed": bootstrap, "aggregate_cross_source_pairs_observed": aggregate_pairs,
               "aggregate_cross_source_pairs_used": aggregate_used_cross,
               "aggregate_false_positives": aggregate_alerts, "gates": gates, "overall_gate": gates["repeatability"] and gates["treatment_integrity"]}
    (out / "raw-results.json").write_text(json.dumps(generated, indent=2))
    (out / "summary.json").write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
