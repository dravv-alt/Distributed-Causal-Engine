import json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parent; OUT=ROOT/"results"/"E039-R001"; DB=OUT/"crash-lab.sqlite"
points=["before_commit","after_commit","before_notification","after_notification","during_lease","after_lease_expiry"]
def connect():
 c=sqlite3.connect(DB); c.execute("PRAGMA journal_mode=WAL")
 c.executescript("CREATE TABLE IF NOT EXISTS inputs(id TEXT PRIMARY KEY); CREATE TABLE IF NOT EXISTS decisions(id TEXT PRIMARY KEY, value TEXT NOT NULL); CREATE TABLE IF NOT EXISTS outbox(id TEXT PRIMARY KEY, sent INTEGER NOT NULL DEFAULT 0); CREATE TABLE IF NOT EXISTS deliveries(id TEXT PRIMARY KEY); CREATE TABLE IF NOT EXISTS leases(id TEXT PRIMARY KEY, owner TEXT, fence INTEGER, expires INTEGER);")
 return c
def recover(c,case):
 if not c.execute("SELECT 1 FROM decisions WHERE id=?",(case,)).fetchone():
  c.execute("BEGIN IMMEDIATE"); c.execute("INSERT INTO decisions VALUES(?,?)",(case,"decision")); c.execute("INSERT INTO outbox(id,sent) VALUES(?,0)",(case,)); c.commit()
 if not c.execute("SELECT sent FROM outbox WHERE id=?",(case,)).fetchone()[0]:
  c.execute("BEGIN IMMEDIATE"); c.execute("INSERT OR IGNORE INTO deliveries VALUES(?)",(case,)); c.execute("UPDATE outbox SET sent=1 WHERE id=?",(case,)); c.commit()
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 if DB.exists(): raise FileExistsError("refusing to overwrite prior crash-lab database")
 c=connect(); c.commit(); stale_rejected=0; trials=[]
 for point in points:
  for i in range(12):
   case=f"{point}-{i:02d}"; c.execute("INSERT INTO inputs VALUES(?)",(case,)); c.commit()
   if point=="before_commit":
    c.execute("BEGIN IMMEDIATE"); c.execute("INSERT INTO decisions VALUES(?,?)",(case,"decision")); c.execute("INSERT INTO outbox(id,sent) VALUES(?,0)",(case,)); c.rollback(); c.close(); c=connect()
   elif point in ("during_lease","after_lease_expiry"):
    c.execute("INSERT OR REPLACE INTO leases VALUES(?,?,?,?)",(case,"worker-a",1,1)); c.commit(); c.close(); c=connect()
    c.execute("UPDATE leases SET owner='worker-b',fence=2,expires=9 WHERE id=? AND expires<=1",(case,)); c.commit()
    row=c.execute("SELECT owner,fence FROM leases WHERE id=?",(case,)).fetchone()
    if row != ("worker-b",2): raise AssertionError("lease recovery failed")
    stale=c.execute("UPDATE leases SET owner='worker-a' WHERE id=? AND fence=1",(case,)); c.commit()
    stale_rejected += int(stale.rowcount==0)
   else:
    c.execute("BEGIN IMMEDIATE"); c.execute("INSERT INTO decisions VALUES(?,?)",(case,"decision")); c.execute("INSERT INTO outbox(id,sent) VALUES(?,0)",(case,)); c.commit()
    if point=="after_notification":
     c.execute("INSERT OR IGNORE INTO deliveries VALUES(?)",(case,)); c.execute("UPDATE outbox SET sent=1 WHERE id=?",(case,)); c.commit()
    c.close(); c=connect()
   recover(c,case)
   d=c.execute("SELECT count(*) FROM decisions WHERE id=?",(case,)).fetchone()[0]; n=c.execute("SELECT count(*) FROM deliveries WHERE id=?",(case,)).fetchone()[0]
   trials.append({"case":case,"point":point,"decisions":d,"deliveries":n,"integrity":c.execute("PRAGMA integrity_check").fetchone()[0]})
 c.close(); summary={"cases":len(trials),"all_one_decision":all(t["decisions"]==1 for t in trials),"all_one_delivery":all(t["deliveries"]==1 for t in trials),"integrity_ok":all(t["integrity"]=="ok" for t in trials),"stale_lease_rejections":stale_rejected,"points":{p:sum(t["point"]==p for t in trials) for p in points},"scope":"local SQLite simulator only"}
 (OUT/"trials.json").write_text(json.dumps(trials,indent=2)+"\n"); (OUT/"metrics.json").write_text(json.dumps(summary,indent=2)+"\n"); print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
