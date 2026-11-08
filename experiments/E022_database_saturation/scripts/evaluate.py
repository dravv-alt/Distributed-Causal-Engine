from __future__ import annotations
import hashlib,json,sqlite3
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E022-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rawpath=RUN/"raw-run.json";raw=json.loads(rawpath.read_text());trials=raw["outcomes"]
    integrity=sqlite3.connect((RUN/"intake.sqlite3").resolve().as_uri()+"?mode=ro",uri=True)
    try:
        integrity_result=integrity.execute("PRAGMA integrity_check").fetchone()[0]
        rows=integrity.execute("SELECT sequence,payload_sha256,duplicate_of_sequence FROM intake_batches ORDER BY sequence").fetchall()
    finally:integrity.close()
    pass_control=sum(t["control"]["status"]==200 for t in trials)
    intervention=sum(t["locked_intervention"]["status"]==503 and t["locked_intervention"]["elapsed_ms"]>=4500 for t in trials)
    retry=sum(t["post_release_retry"]["status"]==200 for t in trials)
    linked=sum(len(t["matching_durable_rows"])==2 and t["matching_durable_rows"][1]["duplicate_of_sequence"]==t["matching_durable_rows"][0]["sequence"] for t in trials)
    result={"experiment":"E022-R001","planning_stage":"XP019","matched_trials":len(trials),"control":{"successful":pass_control,"n":len(trials)},"writer_lock_intervention":{"retryable_503_after_configured_timeout":intervention,"n":len(trials),"median_elapsed_ms":sorted(t["locked_intervention"]["elapsed_ms"] for t in trials)[len(trials)//2]},"post_release_retry":{"successful":retry,"n":len(trials)},"durable_delivery":{"trials_with_original_and_duplicate_retry":linked,"n":len(trials),"total_rows":len(rows),"sqlite_integrity_check":integrity_result,"duplicate_links":sum(r[2] is not None for r in rows)},"interpretation":"Local SQLite write-lock contention reliably produced retryable errors; retry after release was durably stored and linked. Five-pair component experiment, not distributed-system saturation evidence.","provenance":{"raw_run_sha256":sha(rawpath),"database_bytes":(RUN/"intake.sqlite3").stat().st_size}}
    (RUN/"evaluation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
