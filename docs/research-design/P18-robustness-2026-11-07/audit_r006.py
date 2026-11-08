"""Independent read-only audit for P18-R006 saved outputs and provenance."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RUN = HERE / "results" / "P18-R006"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    result = json.loads((RUN / "results.json").read_text(encoding="utf-8"))
    invalids = {"NaN", "Infinity", "-1", "not-a-number"}
    base = result["base_retry_cases"]
    candidate = result["candidate_retry_cases"]
    base_watermark = result["base_watermark_cases"]
    candidate_watermark = result["candidate_watermark_cases"]
    checks = {
        "run_identity": result.get("run_id") == "P18-R006",
        "local_only": result.get("network_access") is False
        and result.get("external_services") is False,
        "complete_invalid_input_matrix": all(
            {row["invalid_value"] for row in rows} == invalids
            for rows in (base, candidate, base_watermark, candidate_watermark)
        ),
        "comparison_reproduces_poisoning": all(
            row["error"]
            and not row["state_unchanged_after_error"]
            and not row["retry_accepted"]
            for row in base
        ),
        "package_candidate_is_transactional": all(
            row["error"]
            and row["state_unchanged_after_error"]
            and row["retry_accepted"]
            and not row["retry_rejected"]
            for row in candidate
        ),
        "candidate_preserves_watermark": all(
            row["state_unchanged_after_error"]
            and row["probe_accepted"]
            and not row["probe_rejection_reasons"]
            for row in candidate_watermark
        ),
        "runner_assertions_reproduced": all(result["assertions"].values())
        and result["candidate_contract_pass"] is True,
    }
    source_paths = {
        "protocol": HERE / "protocol-amendment-r006.md",
        "configuration": HERE / "configuration-r006.json",
        "runner": HERE / "run_r006.py",
        "baseline": REPO / "src/dce_foundation/representation_v2/temporal.py",
        "candidate": REPO / "src/dce_foundation/representation_v2/temporal_transactional.py",
    }
    hash_checks = {
        name: sha(source_paths[name]) == expected
        for name, expected in result["source_sha256"].items()
    }
    checks["source_hashes_match"] = all(hash_checks.values())
    audit = {
        "audit": "P18-R006 independent output/provenance audit",
        "passed": all(checks.values()),
        "checks": checks,
        "source_hash_checks": hash_checks,
        "cases_per_invalid_value": 4,
        "limitations": [
            "Package-level deterministic fixture only; ingest path is not wired to the candidate.",
            "Does not establish real telemetry semantics, temporal validity, RCA quality, or production robustness.",
        ],
    }
    target = RUN / "independent-audit.json"
    if target.exists():
        raise FileExistsError(f"refusing to overwrite {target}")
    target.write_text(json.dumps(audit, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit, indent=2))


if __name__ == "__main__":
    main()
