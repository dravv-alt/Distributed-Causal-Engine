from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/"experiments/E020_remove_temporal";OUT=BASE/"results/E020-R001/artifact-manifest.json"
EXTRA=[ROOT/"EXPERIMENT_INDEX_AMENDMENT_2026-11-07_E020.md",ROOT/"experiments/E017_fusion_ablation/scripts/generate_fixtures.py"]
def main():
    paths=[p for p in BASE.rglob("*") if p.is_file() and p!=OUT]+EXTRA
    files=[{"path":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size} for p in sorted(set(paths))]
    OUT.write_text(json.dumps({"experiment":"E020-R001","planning_stage":"XP017","files":files},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"files_hashed":len(files),"manifest_sha256":hashlib.sha256(OUT.read_bytes()).hexdigest()},indent=2))
if __name__=="__main__":main()
