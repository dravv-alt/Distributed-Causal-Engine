"""Read-only governance consistency checks. No approvals, writes or experiments."""
import argparse
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]


def read_json(root, relative):
    return json.loads((root / relative).read_text(encoding="utf-8"))


def validate_structure(plan, state):
    errors = []
    stages = plan.get("stages", [])
    ids = [s["planning_id"] for s in stages]
    expected = [f"XP{i:03d}" for i in range(1, 39)]
    if sorted(ids) != expected:
        errors.append("expected exactly 38 unique XP planning keys")
    phase_ids = [p["phase_id"] for p in plan.get("phases", [])]
    if phase_ids != [f"P{i:02d}" for i in range(21)]:
        errors.append("expected detailed phases P00..P20")
    if plan.get("decisions") != ["PROCEED", "REVISE", "REPEAT", "BRANCH", "ABANDON"]:
        errors.append("nonstandard decision outcomes")
    lookup = {s["planning_id"]: s for s in stages}
    for s in stages:
        sid = s["planning_id"]
        if s.get("phase_id") not in phase_ids:
            errors.append(f"{sid}: unknown phase")
        if any(dep not in lookup for dep in s.get("depends_on", [])):
            errors.append(f"{sid}: missing prerequisite")
        for field in ("implementation_steps", "controls", "baseline_reference", "metric_families", "required_artifacts", "card"):
            if not s.get(field): errors.append(f"{sid}: missing {field}")
        if s.get("review_status") != "pending" or s.get("approval_reference") is not None:
            errors.append(f"{sid}: adoption checkpoint must not invent approval")
        if s.get("acceptance_thresholds") is not None:
            errors.append(f"{sid}: thresholds were not approved at adoption")
        if s.get("experiment_id") != ("E003" if sid == "XP001" else None):
            errors.append(f"{sid}: unauthorized allocation or permanent-ID remapping")
    visited, active = set(), set()

    def visit(sid):
        if sid in active:
            errors.append("dependency cycle: " + sid)
            return
        if sid in visited: return
        active.add(sid)
        for dep in lookup[sid].get("depends_on", []):
            if dep in lookup: visit(dep)
        active.remove(sid)
        visited.add(sid)

    for sid in lookup: visit(sid)
    if state.get("active_experiment") != "E003" or state.get("active_run") != "E003-R001":
        errors.append("checkpoint active experiment/run drift")
    if state.get("gate_status") != "blocked_review_pending" or state.get("review_status") != "pending":
        errors.append("checkpoint must retain E003 blocked review")
    if state.get("approval_reference") is not None or state.get("authority_to_modify_existing_records"):
        errors.append("checkpoint must not invent approval/edit authority")
    if state.get("next_experiment_allocated"):
        errors.append("successor experiment is not allocated")
    meanings = {e["id"]: e["meaning"] for e in state.get("registered_experiments", [])}
    if meanings != {"E001": "R0 baseline reproduction", "E002": "onset/timing analysis", "E003": "domain model adequacy"}:
        errors.append("permanent experiment meanings changed")
    return errors


def check(root=ROOT):
    plan = read_json(root, "docs/governance/execution-plan.json")
    state = read_json(root, "docs/governance/project-state.json")
    manifest = read_json(root, "docs/governance/preservation-manifest.json")
    errors = validate_structure(plan, state)
    protected = manifest["protected_existing_records"]
    protected = {**protected, manifest["archived_program"]["path"]: manifest["archived_program"]["sha256"]}
    for name, expected in protected.items():
        path = root / name
        if not path.is_file(): errors.append("missing protected record: " + name)
        elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
            errors.append("protected content changed: " + name)
    for stage in plan["stages"]:
        if not (root / stage["card"]).is_file(): errors.append("missing stage card: " + stage["card"])
    for path in state["evidence"].values():
        if not (root / path).is_file(): errors.append("missing evidence: " + path)
    actual = read_json(root, state["evidence"]["results"])
    facts = state["verified_checkpoint_facts"]
    reports = actual["reports"]
    if actual.get("downstream_ready") or not actual.get("review_required"):
        errors.append("live E003 result conflicts with blocked checkpoint")
    if len(reports) != facts["scope_replays"] or not actual.get("all_deterministic"):
        errors.append("checkpoint replay count/determinism drift")
    for key in ("source_rows_scanned", "source_rows_mapped", "source_rows_rejected", "source_rows_outside_window"):
        if sum(r[key] for r in reports) != facts[key]: errors.append("checkpoint total mismatch: " + key)
    if sum(r["observations"] for r in reports) != facts["canonical_observations"]:
        errors.append("checkpoint observation total mismatch")
    # Check local Markdown links only; no network, environment mutation or archive reads.
    documents = [root / name for name in ("AGENTS.md", "EXPERIMENTAL_PROTOCOL.md", "PROJECT_STATE.md")]
    documents += list((root / "docs/governance").rglob("*.md"))
    for doc in documents:
        if doc.name == "EXECUTION_PROGRAM_ORIGINAL.md": continue
        for target in re.findall(r"\]\(([^)]+)\)", doc.read_text(encoding="utf-8")):
            if target.startswith(("http:", "https:", "#")): continue
            target = target.split("#", 1)[0]
            if not (doc.parent / target).exists(): errors.append(f"broken link in {doc.relative_to(root)}: {target}")
    return errors, len(protected), len(plan["stages"])


def self_test():
    plan = read_json(ROOT, "docs/governance/execution-plan.json")
    state = read_json(ROOT, "docs/governance/project-state.json")
    assert not validate_structure(plan, state)
    modified = deepcopy(plan)
    modified["stages"][1]["experiment_id"] = "E004"
    assert validate_structure(modified, state)
    modified = deepcopy(plan)
    modified["stages"][0]["depends_on"] = ["XP038"]
    assert any("cycle" in e for e in validate_structure(modified, state))
    modified_state = deepcopy(state)
    modified_state["gate_status"] = "approved"
    assert validate_structure(plan, modified_state)
    print("Self-test PASS: unauthorized allocation, dependency cycles and false gate promotion rejected")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test: self_test()
    errors, preserved, stages = check()
    if errors:
        for error in errors: print("FAIL:", error)
        raise SystemExit(1)
    print(f"PASS: {preserved} protected files unchanged; {stages} stages; links, dependency graph and checkpoint consistent")
    print("E003 gate: BLOCKED / HUMAN REVIEW PENDING. Consistency is not approval or physical immutability.")


if __name__ == "__main__": main()
