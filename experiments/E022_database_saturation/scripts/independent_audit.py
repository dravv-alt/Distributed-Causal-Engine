from __future__ import annotations
import hashlib,json,sqlite3
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E022-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rawpath=RUN/"raw-run.json";raw=json.loads(rawpath.read_text());rows=raw["outcomes"]
    db=sqlite3.connect((RUN/"intake.sqlite3").resolve().as_uri()+"?mode=ro",uri=True)
    try:
        integrity=db.execute("PRAGMA integrity_check").fetchone()[0]
        stored=db.execute("SELECT sequence,payload_sha256,duplicate_of_sequence FROM intake_batches ORDER BY sequence").fetchall()
    finally:db.close()
    assert len(rows)==5 and integrity=="ok" and len(stored)==10
    for t in rows:
        assert t["control"]["status"]==200
        assert t["locked_intervention"]["status"]==503 and t["locked_intervention"]["elapsed_ms"]>=4500
        assert t["post_release_retry"]["status"]==200
        matches=[r for r in stored if r[1]==t["payload_sha256"]]
        assert len(matches)==2 and matches[0][2] is None and matches[1][2]==matches[0][0]
    report=json.loads((RUN/"evaluation.json").read_text())
    assert report["control"]["successful"]==5 and report["writer_lock_intervention"]["retryable_503_after_configured_timeout"]==5
    assert report["post_release_retry"]["successful"]==5 and report["durable_delivery"]["trials_with_original_and_duplicate_retry"]==5
    audit={"audit":"E022-R001 independent database and response audit","passed":True,"checks":["5/5 no-lock controls return 200","5/5 held writer locks return 503 after >=4.5 seconds","5/5 retries return 200 after lock release","5/5 duplicate rows link to original durable sequence","SQLite integrity_check is ok"],"sqlite_rows":len(stored),"hashes":{"raw_run":sha(rawpath),"database":sha(RUN/"intake.sqlite3"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8");print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
