from __future__ import annotations

import argparse
import json
import sys

from . import __version__
from .simulator import Dataset, SimConfig, simulate
from .topology import layered_topology, reference_topology


def _topology(spec: str):
    if spec == "reference":
        return reference_topology()
    kind, n, seed = spec.split(":")  # layered:N:seed
    assert kind == "layered"
    return layered_topology(int(n), int(seed))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="dce")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("simulate", help="generate a labeled synthetic dataset")
    s.add_argument("--out", required=True); s.add_argument("--seed", type=int, default=0)
    s.add_argument("--duration", type=int, default=20000); s.add_argument("--topology", default="reference")
    s.add_argument("--no-faults", action="store_true"); s.add_argument("--load-scale", type=float, default=1.0)
    s.add_argument("--missing-rate", type=float, default=0.0); s.add_argument("--env-seed", type=int, default=None)
    s.add_argument("--mean-gap", type=float, default=700.0); s.add_argument("--p-concurrent", type=float, default=0.10)
    t = sub.add_parser("train", help="train a model bundle on a dataset's chronological train segment")
    t.add_argument("--data", required=True); t.add_argument("--out", required=True); t.add_argument("--seed", type=int, default=0)
    e = sub.add_parser("eval", help="evaluate baselines, hybrid and ablations")
    e.add_argument("--bundle", required=True); e.add_argument("--data", nargs="*", default=[], help="in-distribution: test segment")
    e.add_argument("--heldout", nargs="*", default=[], help="held-out seed/workload: whole dataset")
    e.add_argument("--faultfree", nargs="*", default=[]); e.add_argument("--out", default=None)
    sub.add_parser("version")
    a = p.parse_args(argv)

    if a.cmd == "version":
        print(__version__); return 0
    if a.cmd == "simulate":
        cfg = SimConfig(duration_s=a.duration, seed=a.seed, env_seed=a.env_seed, with_faults=not a.no_faults,
                        load_scale=a.load_scale, missing_rate=a.missing_rate,
                        mean_gap_s=a.mean_gap, p_concurrent=a.p_concurrent)
        ds = simulate(_topology(a.topology), cfg)
        ds.save(a.out)
        print(f"wrote {a.out}: {len(ds.times)} steps, {len(ds.topology.services)} services, {len(ds.events)} faults")
        return 0
    from .neural import ModelBundle
    if a.cmd == "train":
        from .train import train_bundle
        b = train_bundle(Dataset.load(a.data), seed=a.seed)
        b.save(a.out)
        print(f"wrote bundle {a.out}: {b.model_version}, threshold={b.manifest['neural_threshold']:.3f}, "
              f"val window F1={b.manifest['training']['val_window_f1']}")
        return 0
    if a.cmd == "eval":
        from .evaluate import evaluate_dataset, false_alert_rate, format_report
        from .schema import FeatureSchema
        from .windows import chronological_segments
        b = ModelBundle.load(a.bundle)
        sp = b.manifest["split"]
        report = {"model_version": b.model_version, "note": "synthetic data; not evidence of real-world accuracy",
                  "datasets": {}, "false_alerts": {}}
        for path, held in [(d, False) for d in a.data] + [(d, True) for d in a.heldout]:
            ds = Dataset.load(path)
            b.check_compatible(ds.topology, FeatureSchema())
            T = len(ds.times)
            lo, hi = (0, T) if held else chronological_segments(T, tuple(sp["fractions"]), sp["embargo"])["test"]
            res = evaluate_dataset(ds, lo, hi, b, context=sp["context"], stride=sp["stride"])
            report["datasets"][path] = {"range": [lo, hi], "heldout": held, "results": res}
            print(format_report(f"{path} ({'held-out' if held else 'chronological test'}, steps {lo}-{hi})", res), "\n")
        for path in a.faultfree:
            ds = Dataset.load(path)
            b.check_compatible(ds.topology, FeatureSchema())
            report["false_alerts"][path] = false_alert_rate(ds, b, context=sp["context"], stride=sp["stride"])
            print(f"fault-free {path}:", json.dumps(report["false_alerts"][path]))
        if a.out:
            open(a.out, "w").write(json.dumps(report, indent=1))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
