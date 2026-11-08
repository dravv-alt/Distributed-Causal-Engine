from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/"experiments"/"E018_remove_neural"
OUTPUT=BASE/"results"/"E018-R001"/"artifact-manifest.json"
EXTRA=[ROOT/"EXPERIMENT_INDEX_AMENDMENT_2026-11-07_E018.md",ROOT/"experiments/E017_fusion_ablation/scripts/generate_fixtures.py"]


def main():
    paths=[p for p in BASE.rglob("*") if p.is_file() and p!=OUTPUT]+EXTRA
    items=[{"path":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size} for p in sorted(set(paths))]
    OUTPUT.write_text(json.dumps({"experiment":"E018-R001","planning_stage":"XP015","files":items},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"files_hashed":len(items),"manifest_sha256":hashlib.sha256(OUTPUT.read_bytes()).hexdigest()},indent=2))


if __name__=="__main__":main()
