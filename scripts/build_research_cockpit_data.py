"""Build read-only, normalized Research Cockpit data from DCE experiment artifacts.

This adapter is intentionally presentation-only. It neither executes experiments
nor edits their records. Plain-language fields explain documented findings; all
measured claims link back to the source artifacts listed in each summary.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "frontend" / "research-cockpit" / "data" / "experiments.json"


def read_json(relative: str) -> dict:
    path = ROOT / relative
    if not path.exists():
        raise FileNotFoundError(f"Required cockpit source is missing: {relative}")
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def artifact(label: str, relative: str) -> dict:
    path = ROOT / relative
    return {"label": label, "path": relative.replace("\\", "/"), "sha256": sha256(relative) if path.is_file() else None}


def build() -> dict:
    e001_manifest = read_json("experiments/E001/results/E001-R001/artifact-manifest.json")
    e002_summary = read_json("experiments/E002/results/E002-R001/summary.json")
    e002_config = read_json("experiments/E002/results/E002-R001/frozen-configuration.json")
    e003_decision = ROOT / "experiments/E003_domain_model_adequacy/decision.md"
    if not e003_decision.exists():
        raise FileNotFoundError("Required cockpit source is missing: E003 decision")

    e001_reproduced = e001_manifest["comparison"]["result_table_mismatches"] == []
    repeatable = e002_summary["gates"]["repeatability"]
    integrity = e002_summary["gates"]["treatment_integrity"]
    superiority = e002_summary["gates"]["superiority"]

    return {
        "schema_version": "dce.research-cockpit.v1",
        "generated_from": "read-only local experiment artifacts",
        "current_stage": {
            "title": "Checking whether the research method is trustworthy",
            "plain": "DCE is not at automatic fixing. We are checking whether its tests, data, and explanations are reliable enough to support later diagnosis work.",
            "status": "BLOCKED"
        },
        "experiments": [
            {
                "experiment_id": "E001", "run_id": "E001-R001", "status": "REVIEW", "decision": "REVISE",
                "question": "Can we repeat the original simulated DCE demo?",
                "what_we_did": "Ran the original synthetic-data recipe again in a new folder and compared its five result tables with the delivered report.",
                "result": "PASS: the five comparable result tables matched the delivered report.",
                "blocking": "It blocks E002 only until a human accepts the proposed REVISE decision and asks for the repeatability gate to be cleaned up.",
                "meaning": "The old simulated demo is repeatable once on this machine.",
                "not_established": "It does not prove DCE works on real outages, and it does not prove the hybrid approach is better than its simpler alternatives.",
                "waiting": "Human review of the proposed REVISE decision: keep R0 as a baseline, but require a cleaner repeatability/test gate.",
                "facts": [
                    f"Reproduction CLI completed: {'yes' if e001_reproduced else 'no'}.",
                    "Five comparable tables had zero mismatches after output-path normalization.",
                    "47 repository tests passed in the reviewed workspace check."
                ],
                "artifacts": [artifact("Run summary", "experiments/E001/results/E001-R001/SUMMARY.md"), artifact("Execution record", "experiments/E001/logs/E001-R001.md"), artifact("Raw report", "experiments/E001/results/E001-R001/report.json")]
            },
            {
                "experiment_id": "E002", "run_id": "E002-R001", "status": "REVIEW", "decision": "REVISE",
                "question": "Does using consistent timing sources improve which component is ranked as the likely root cause?",
                "what_we_did": "Repeated the same synthetic test three times, then compared current mixed timing, same-source-only timing, and timing-disabled policies over five fixed held-out seeds.",
                "result": "Repeatability PASS; treatment integrity PASS; superiority FAIL; environment qualification FAIL.",
                "blocking": "It is stopped for review. Do not claim improvement or change the experiment after seeing these results.",
                "meaning": "The exact test repeated consistently, but the tested timing cleanup did not improve root-cause ranking in this simulator.",
                "not_established": "It does not prove timing is useless, the hybrid is useless, or that a differently controlled timing method can never help.",
                "waiting": "Human review of REVISE: pin compatible software versions and hardware details before any separately approved rerun.",
                "facts": [
                    f"Three canonical result hashes were identical: {'yes' if repeatable else 'no'}.",
                    f"Same-source timing used zero cross-source pairs: {'yes' if integrity else 'no'}.",
                    f"Paired Top-1 difference was {e002_summary['paired_top1_same_source_minus_mixed']['mean']:.3f} across {e002_summary['paired_top1_same_source_minus_mixed']['n_events']} events.",
                    "The active NumPy/SciPy environment emitted a compatibility warning."
                ],
                "gates": [
                    {"name": "Repeatability", "status": "PASS" if repeatable else "FAIL"},
                    {"name": "Treatment integrity", "status": "PASS" if integrity else "FAIL"},
                    {"name": "Superiority", "status": "PASS" if superiority else "FAIL"},
                    {"name": "Environment qualification", "status": "FAIL"}
                ],
                "artifacts": [artifact("Plain result table", "experiments/E002/results/E002-R001/derived-metrics.md"), artifact("Decision proposal", "experiments/E002/results/E002-R001/decision-proposal.md"), artifact("Frozen configuration", "experiments/E002/results/E002-R001/frozen-configuration.json"), artifact("Raw results", "experiments/E002/results/E002-R001/raw-results.json")],
                "technical": {"configuration_sha256": sha256("experiments/E002/results/E002-R001/frozen-configuration.json"), "summary_sha256": sha256("experiments/E002/results/E002-R001/summary.json"), "runner": e002_config["experiment_runner"]}
            },
            {
                "experiment_id": "E003", "run_id": "E003-R001", "status": "BLOCKED", "decision": "REVISE",
                "question": "Can DCE represent the available real OpenRCA incident data without losing information needed for later diagnosis?",
                "what_we_did": "Read and replay bounded samples from the available OpenRCA systems, then checked timestamps, service identities, topology evidence, and labels.",
                "result": "BLOCKED: the representation foundation works, but real-data adequacy is not established.",
                "blocking": "Yes. Do not build real-data RCA, causal reasoning, or self-healing on this representation yet.",
                "meaning": "We found the data problems before building a misleading diagnosis engine.",
                "not_established": "It does not prove DCE can identify the true cause of a real outage or recommend a safe production action.",
                "waiting": "Human review of the recorded data-model revisions; E003 itself must remain unchanged until separately authorized work begins.",
                "facts": ["Timestamp units are inconsistent in some Bank trace files.", "Topology and metric meaning are incomplete for downstream reasoning.", "Bounded replay was deterministic, but bounded replay is not full-dataset adequacy."],
                "artifacts": [artifact("Decision gate", "experiments/E003_domain_model_adequacy/decision.md"), artifact("Implementation report", "docs/E003-implementation-report.md"), artifact("E003 run record", "experiments/E003_domain_model_adequacy/run.md")]
            }
        ],
        "incident_example": {
            "observed": ["1,000 requests arrive.", "The database receives too much work.", "Database latency rises.", "The application server begins failing requests."],
            "possible_causes": ["Normal traffic spike", "Slow database query", "Database capacity limit", "Many requests from one suspicious IP"],
            "possible_actions": ["Add caching", "Scale the database", "Improve the slow query", "Rate-limit requests", "Investigate suspicious IPs"],
            "warning": "This is an educational example. DCE must show evidence before a human chooses an action; it must not automatically declare one action correct."
        }
    }


if __name__ == "__main__":
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    print(OUT.relative_to(ROOT))
