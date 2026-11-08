"""Execute E007's deterministic online/offline event-time comparison."""
from __future__ import annotations

import hashlib
import json
import platform
import sys
import zipfile
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXP = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))
from dce_foundation.representation_v2.temporal import EventTimeWindowAccumulator, TimedSample

RUN = EXP / "results" / "E007-R001"
CONFIG = json.loads((EXP / "configuration.json").read_text(encoding="utf-8"))
MODULE = ROOT / "src" / "dce_foundation" / "representation_v2" / "temporal.py"


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def write_new(path: Path, value: object) -> None:
    with path.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")


def samples() -> list[TimedSample]:
    output = []
    for i in range(CONFIG["event_count_in_window"]):
        value = None if i == 5 else str(i if i < 10 else i - 10)
        output.append(TimedSample(f"e{i:03d}", "synthetic.requests", i * CONFIG["event_spacing_ns"], value))
    return output


def online(schedule: list[TimedSample]) -> dict:
    acc = EventTimeWindowAccumulator(CONFIG["start_ns"], CONFIG["end_ns"],
                                     CONFIG["window_ns"], CONFIG["allowed_lateness_ns"])
    for event in schedule:
        acc.ingest(event)
    boundary = TimedSample("boundary-end", "synthetic.requests", CONFIG["end_ns"], "10")
    acc.ingest(boundary)
    return acc.result()


def offline_oracle(accepted: list[TimedSample], rejected: list[dict]) -> dict:
    """Independent batch computation; deliberately does not call accumulator code."""
    windows = {}
    last = {}
    ordered = sorted(accepted, key=lambda e: (e.event_ns, e.series_id, e.event_id))
    for event in ordered:
        bucket = (event.event_ns // CONFIG["window_ns"]) * CONFIG["window_ns"]
        row = windows.setdefault(bucket, {
            "start_ns": bucket, "end_ns": bucket + CONFIG["window_ns"],
            "observation_mask": 0, "value_mask": 0, "sample_count": 0,
            "valid_value_count": 0, "missing_value_count": 0,
            "counter_delta_count": 0, "counter_delta_total": Decimal(0), "reset_count": 0,
        })
        row["observation_mask"] = 1
        row["sample_count"] += 1
        if event.value is None:
            row["missing_value_count"] += 1
            continue
        row["value_mask"] = 1
        row["valid_value_count"] += 1
        value = Decimal(event.value)
        prior = last.get(event.series_id)
        if prior is None:
            last[event.series_id] = value
            continue
        if value < prior:
            increment = value
            row["reset_count"] += 1
        else:
            increment = value - prior
        last[event.series_id] = value
        row["counter_delta_total"] += increment
        row["counter_delta_count"] += 1

    output_windows = []
    for start in range(CONFIG["start_ns"], CONFIG["end_ns"], CONFIG["window_ns"]):
        row = windows.get(start, {
            "start_ns": start, "end_ns": start + CONFIG["window_ns"],
            "observation_mask": 0, "value_mask": 0, "sample_count": 0,
            "valid_value_count": 0, "missing_value_count": 0,
            "counter_delta_count": 0, "counter_delta_total": Decimal(0), "reset_count": 0,
        })
        row = dict(row)
        row["counter_delta_total"] = str(row["counter_delta_total"])
        output_windows.append(row)
    return {"windows": output_windows,
            "accepted_ids": sorted(e.event_id for e in accepted), "rejected": rejected}


def run_schedule(name: str, schedule: list[TimedSample]) -> dict:
    output = online(schedule)
    accepted_lookup = {event.event_id: event for event in schedule}
    accepted = [accepted_lookup[event_id] for event_id in output["accepted_ids"]]
    oracle = offline_oracle(accepted, output["rejected"])
    return {"name": name, "online": output, "offline_oracle": oracle,
            "exact_match": output == oracle}


def main() -> None:
    RUN.mkdir(parents=True, exist_ok=False)
    relevant = [EXP / "README.md", EXP / "hypothesis.md", EXP / "protocol.md",
                EXP / "configuration.json", Path(__file__), MODULE]
    with zipfile.ZipFile(RUN / "source-snapshot.zip", "x", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in relevant:
            archive.write(path, path.relative_to(ROOT).as_posix())
    git_head = __import__("subprocess").run(["git", "rev-parse", "HEAD"], cwd=ROOT,
                                            capture_output=True, text=True).stdout.strip() or "UNKNOWN"
    git_status = __import__("subprocess").run(["git", "status", "--short"], cwd=ROOT,
                                              capture_output=True, text=True).stdout.splitlines()
    preflight = {"experiment_id": "E007", "run_id": "E007-R001", "git_head": git_head,
                 "git_status_excerpt": git_status[:100], "python": sys.version,
                 "platform": platform.platform(), "network_access": "none",
                 "openresearch": "orx unavailable; local runner",
                 "source_hashes": {path.relative_to(ROOT).as_posix(): sha256(path) for path in relevant},
                 "source_snapshot_sha256": sha256(RUN / "source-snapshot.zip"),
                 "configuration_sha256": sha256(EXP / "configuration.json"),
                 "protocol_sha256": sha256(EXP / "protocol.md")}
    write_new(RUN / "preflight.json", preflight)

    original = samples()
    ordered = original
    bounded = original.copy()
    for i in range(1, len(bounded), 4):
        if i + 1 < len(bounded):
            bounded[i], bounded[i + 1] = bounded[i + 1], bounded[i]
    beyond = original[1:] + [original[0]]
    runs = [run_schedule("ordered-control", ordered),
            run_schedule("bounded-adjacent-reordering", bounded),
            run_schedule("beyond-bound-late-event", beyond)]
    order_invariant = (runs[0]["online"]["accepted_ids"] == runs[1]["online"]["accepted_ids"]
                       and runs[0]["online"]["windows"] == runs[1]["online"]["windows"])
    control = runs[0]["online"]
    late_reasons = {r["event_id"]: r["reason"] for r in runs[2]["online"]["rejected"]}
    second_window = control["windows"][1]
    assertions = {
        "all_three_match_offline_oracle": all(run["exact_match"] for run in runs),
        "ordered_equals_bounded_disorder": order_invariant,
        "missing_value_preserved_without_imputation": (control["windows"][0]["missing_value_count"] == 1
                                                        and control["windows"][0]["sample_count"] == 10),
        "one_reset_in_second_window": second_window["reset_count"] == 1,
        "counter_delta_total_is_18": sum(Decimal(w["counter_delta_total"]) for w in control["windows"]) == Decimal(18),
        "exclusive_end_boundary_rejected": any(r["event_id"] == "boundary-end" and r["reason"] == "out_of_window"
                                                for r in control["rejected"]),
        "oldest_event_rejected_beyond_bound": late_reasons.get("e000") == "beyond_allowed_lateness",
        "late_schedule_has_explicit_rejection": bool(runs[2]["online"]["rejected"]),
    }
    result = {"experiment_id": "E007", "run_id": "E007-R001",
              "status": "PASS" if all(assertions.values()) else "REVISE",
              "assertions": assertions, "schedules": runs,
              "input_event_count": len(original), "synthetic_counter_semantics": "explicitly defined in protocol",
              "limitations": ["Synthetic algorithm prototype only; no production/application integration.",
                             "One series and two windows do not characterize real telemetry.",
                             "Bounded lateness policy necessarily rejects sufficiently old arrivals.",
                             "No RCA diagnosis or detector quality is evaluated."]}
    write_new(RUN / "results.json", result)
    write_new(RUN / "source-manifest.json", {
        "preflight_sha256": sha256(RUN / "preflight.json"),
        "results_sha256": sha256(RUN / "results.json"),
        "snapshot_sha256": sha256(RUN / "source-snapshot.zip"),
        "run_mode": "standalone local; no network; OpenResearch not used",
    })
    print(json.dumps({"status": result["status"], "assertions": assertions,
                      "output": str(RUN / "results.json")}, sort_keys=True))
    if not all(assertions.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
