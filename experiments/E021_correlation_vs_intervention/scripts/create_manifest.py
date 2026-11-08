from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/"experiments/E021_correlation_vs_intervention";OUT=BASE/"results/E021-R001/artifact-manifest.json"
EXTRA=[ROOT/"EXPERIMENT_INDEX_AMENDMENT_2026-11-07_E021.md"]
def main():
    paths=[p for p in BASE.rglob("*") if p.is_file() and p!=OUT]+EXTRA
    fs=[{"path":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size} for p in sorted(set(paths))]
    OUT.write_text(json.dumps({"experiment":"E021-R001","planning_stage":"XP018","files":fs},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"files_hashed":len(fs),"manifest_sha256":hashlib.sha256(OUT.read_bytes()).hexdigest()},indent=2))
if __name__=="__main__":main()
