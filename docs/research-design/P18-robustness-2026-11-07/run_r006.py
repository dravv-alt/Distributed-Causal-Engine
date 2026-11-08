"""Run the frozen P18-R006 invalid-input transactionality cases locally."""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OUT = HERE / "results" / "P18-R006"
sys.path.insert(0, str(REPO / "src"))

from dce_foundation.representation_v2.temporal import (  # noqa: E402
    EventTimeWindowAccumulator,
    TimedSample,
)
from dce_foundation.representation_v2.temporal_transactional import (  # noqa: E402
    TransactionalEventTimeWindowAccumulator,
)

INVALIDS = ("NaN", "Infinity", "-1", "not-a-number")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot(accumulator) -> dict:
    return {
        "accepted": [sample.__dict__ for sample in accumulator.accepted],
        "rejected": list(accumulator.rejected),
        "seen_ids": sorted(accumulator._seen_ids),
        "max_seen_ns": accumulator._max_seen_ns,
    }


def exercise(accumulator_type, invalid_value: str, watermark_probe: bool) -> dict:
    acc = accumulator_type(0, 20, 10, 0)
    acc.ingest(TimedSample("baseline", "series", 2, "1"))
    before = snapshot(acc)
    error = None
    try:
        acc.ingest(TimedSample("repair", "series", 15, invalid_value))
    except ValueError as exc:
        error = str(exc)
    after_error = snapshot(acc)
    if watermark_probe:
        acc.ingest(TimedSample("probe", "series", 3, "2"))
        return {
            "invalid_value": invalid_value,
            "error": error,
            "state_unchanged_after_error": before == after_error,
            "probe_accepted": "probe" in {x.event_id for x in acc.accepted},
            "probe_rejection_reasons": [x["reason"] for x in acc.rejected],
            "before": before,
            "after_error": after_error,
        }

    acc.ingest(TimedSample("repair", "series", 15, "2"))
    return {
        "invalid_value": invalid_value,
        "error": error,
        "state_unchanged_after_error": before == after_error,
        "retry_accepted": "repair" in {x.event_id for x in acc.accepted},
        "retry_rejected": [x for x in acc.rejected if x["event_id"] == "repair"],
        "before": before,
        "after_error": after_error,
    }


def main() -> None:
    if (OUT / "results.json").exists():
        raise FileExistsError(f"refusing to overwrite {OUT / 'results.json'}")
    base_retry = [exercise(EventTimeWindowAccumulator, value, False) for value in INVALIDS]
    candidate_retry = [
        exercise(TransactionalEventTimeWindowAccumulator, value, False)
        for value in INVALIDS
    ]
    base_watermark = [exercise(EventTimeWindowAccumulator, value, True) for value in INVALIDS]
    candidate_watermark = [
        exercise(TransactionalEventTimeWindowAccumulator, value, True)
        for value in INVALIDS
    ]

    assertions = {
        "base_reproduces_seen_id_poisoning": all(
            row["error"] and not row["state_unchanged_after_error"] and not row["retry_accepted"]
            for row in base_retry
        ),
        "candidate_errors_are_transactional": all(
            row["error"] and row["state_unchanged_after_error"] and row["retry_accepted"]
            for row in candidate_retry
        ),
        "candidate_preserves_watermark": all(
            row["state_unchanged_after_error"] and row["probe_accepted"]
            for row in candidate_watermark
        ),
        "all_error_classes_observed": all(row["error"] for row in base_retry + candidate_retry),
    }
    sources = {
        "protocol": HERE / "protocol-amendment-r006.md",
        "configuration": HERE / "configuration-r006.json",
        "runner": Path(__file__).resolve(),
        "baseline": REPO / "src/dce_foundation/representation_v2/temporal.py",
        "candidate": REPO / "src/dce_foundation/representation_v2/temporal_transactional.py",
    }
    result = {
        "run_id": "P18-R006",
        "planning_phase": "P18 robustness follow-up",
        "network_access": False,
        "external_services": False,
        "invalid_values": list(INVALIDS),
        "base_retry_cases": base_retry,
        "candidate_retry_cases": candidate_retry,
        "base_watermark_cases": base_watermark,
        "candidate_watermark_cases": candidate_watermark,
        "assertions": assertions,
        "candidate_contract_pass": all(assertions.values()),
        "source_sha256": {name: sha(path) for name, path in sources.items()},
        "environment": {"python": sys.version, "platform": platform.platform()},
        "interpretation_limit": "package behavior on deterministic local fixtures; ingest path not wired",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "results.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"run_id": result["run_id"], "assertions": assertions}, indent=2))


if __name__ == "__main__":
    main()
