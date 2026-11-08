"""Read-only independent audit of the preserved E007-R001 synthetic output."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
RUN = ROOT / "experiments/E007_temporal_correctness/results/E007-R001"
OUT = RUN / "independent-audit-addendum-2026-11-08.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    preflight_path = RUN / "preflight.json"
    results_path = RUN / "results.json"
    snapshot_path = RUN / "source-snapshot.zip"
    manifest_path = RUN / "source-manifest.json"
    preflight = json.loads(preflight_path.read_text(encoding="utf-8"))
    results = json.loads(results_path.read_text(encoding="utf-8"))
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    schedules = results["schedules"]

    checks = {
        "preflight_hash_matches_manifest": sha256(preflight_path) == manifest["preflight_sha256"],
        "result_hash_matches_manifest": sha256(results_path) == manifest["results_sha256"],
        "snapshot_hash_matches_both_records": (
            sha256(snapshot_path) == manifest["snapshot_sha256"] == preflight["source_snapshot_sha256"]
        ),
        "all_frozen_source_hashes_match": all(
            (ROOT / relative).is_file() and sha256(ROOT / relative) == expected
            for relative, expected in preflight["source_hashes"].items()
        ),
        "all_three_saved_oracle_pairs_match": all(
            item["online"] == item["offline_oracle"] and item["exact_match"]
            for item in schedules
        ),
        "schedule_accepted_counts_are_20_20_19": [
            len(item["online"]["accepted_ids"]) for item in schedules
        ] == [20, 20, 19],
        "ordered_and_bounded_outputs_match": schedules[0]["online"] == schedules[1]["online"],
        "late_event_has_explicit_rejection": any(
            item == {"event_id": "e000", "reason": "beyond_allowed_lateness"}
            for item in schedules[2]["online"]["rejected"]
        ),
        "ordered_window_counts_match_frozen_fixture": [
            (
                window["sample_count"],
                window["valid_value_count"],
                window["missing_value_count"],
                window["counter_delta_total"],
                window["reset_count"],
            )
            for window in schedules[0]["online"]["windows"]
        ] == [(10, 9, 1, "9", 0), (10, 10, 0, "9", 1)],
        "protocol_deviation_is_preserved": (RUN / "protocol-deviation.md").is_file(),
    }

    payload = {
        "audit": "E007-R001 saved-output integrity and fixture consistency",
        "audit_date": "2026-11-08",
        "scope": "Read-only verification of saved files; no experiment rerun",
        "source_files": {
            path.relative_to(ROOT).as_posix(): sha256(path)
            for path in (preflight_path, results_path, snapshot_path, manifest_path)
        },
        "verifier": Path(__file__).relative_to(ROOT).as_posix(),
        "verifier_sha256": sha256(Path(__file__)),
        "checks": checks,
        "passed": sum(value is True for value in checks.values()),
        "total": len(checks),
        "interpretation_limit": (
            "This checks the preserved synthetic fixture outputs and their hashes. "
            "It does not validate real telemetry, DCE application integration, or RCA quality."
        ),
    }
    with OUT.open("x", encoding="utf-8", newline="\n") as stream:
        json.dump(payload, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps({"passed": payload["passed"], "total": payload["total"], "output": str(OUT)}))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
