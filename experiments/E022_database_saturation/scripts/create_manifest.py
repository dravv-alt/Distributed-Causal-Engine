from __future__ import annotations
import hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/"experiments/E022_database_saturation";OUT=BASE/"results/E022-R001/artifact-manifest.json"
EXTRA=[ROOT/"EXPERIMENT_INDEX_AMENDMENT_2026-11-07_E022.md",ROOT/"src/dce_foundation/ingest/app.py",ROOT/"src/dce_foundation/ingest/store.py",ROOT/"src/dce_foundation/ingest/otlp.py"]
def main():
    ps=[p for p in BASE.rglob("*") if p.is_file() and p!=OUT]+EXTRA
    fs=[{"path":p.relative_to(ROOT).as_posix(),"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"bytes":p.stat().st_size} for p in sorted(set(ps))]
    OUT.write_text(json.dumps({"experiment":"E022-R001","planning_stage":"XP019","files":fs},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"files_hashed":len(fs),"manifest_sha256":hashlib.sha256(OUT.read_bytes()).hexdigest()},indent=2))
if __name__=="__main__":main()
