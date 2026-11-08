from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "experiments" / "E016_membership_adaptation"
OUTPUT = BASE / "results" / "E016-R001" / "artifact-manifest.json"
EXTRA = [ROOT / "EXPERIMENT_INDEX_AMENDMENT_2026-11-07_E016.md", ROOT / "src/dce_foundation/representation_v2/service_membership.py"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    paths = sorted(p for p in BASE.rglob("*") if p.is_file() and p != OUTPUT)
    paths.extend(EXTRA)
    rows = [{"path": p.relative_to(ROOT).as_posix(), "sha256": digest(p), "bytes": p.stat().st_size} for p in sorted(set(paths))]
    result = {"experiment": "E016-R001", "planning_stage": "XP013", "files": rows}
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"files_hashed": len(rows), "manifest_sha256": digest(OUTPUT), "manifest": OUTPUT.relative_to(ROOT).as_posix()}, indent=2))


if __name__ == "__main__":
    main()
