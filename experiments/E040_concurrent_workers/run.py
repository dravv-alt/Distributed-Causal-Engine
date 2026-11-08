import sqlite3,threading,time,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent; OUT=ROOT/"results"/"E040-R001"; DB=OUT/"workers.sqlite"
def conn():
 c=sqlite3.connect(DB,timeout=20); c.execute("PRAGMA journal_mode=WAL"); c.execute("PRAGMA busy_timeout=20000"); return c
def init():
 c=conn(); c.executescript("CREATE TABLE tasks(id TEXT PRIMARY KEY,status TEXT,owner TEXT,fence INTEGER,lease_until REAL); CREATE TABLE executions(id INTEGER PRIMARY KEY,task TEXT,worker TEXT); CREATE TABLE decisions(task TEXT PRIMARY KEY,worker TEXT,fence INTEGER);")
 for prefix in ("single","concurrent"):
  c.executemany("INSERT INTO tasks VALUES(?, 'pending', NULL, 0, 0)",[(f"{prefix}-{i:03d}",) for i in range(100)])
 c.execute("INSERT INTO tasks VALUES('stale-case','pending',NULL,0,0)"); c.commit(); c.close()
def claim(worker,prefix=None):
 c=conn(); c.execute("BEGIN IMMEDIATE")
 q="SELECT id,fence FROM tasks WHERE (status='pending' OR (status='leased' AND lease_until<?))"; args=(time.time(),)
 if prefix: q+=" AND id LIKE ?"; args+=(prefix+"-%",)
 q+=" ORDER BY id LIMIT 1"; row=c.execute(q,args).fetchone()
 if not row: c.commit(); c.close(); return None
 task,fence=row; fence+=1; c.execute("UPDATE tasks SET status='leased',owner=?,fence=?,lease_until=? WHERE id=?",(worker,fence,time.time()+30,task)); c.commit(); c.close(); return task,fence
def finish(worker,task,fence,record=True):
 c=conn(); c.execute("BEGIN IMMEDIATE"); row=c.execute("SELECT owner,fence,status FROM tasks WHERE id=?",(task,)).fetchone()
 if row!=(worker,fence,"leased"): c.rollback(); c.close(); return False
 if record: c.execute("INSERT INTO executions(task,worker) VALUES(?,?)",(task,worker))
 c.execute("UPDATE tasks SET status='done' WHERE id=?",(task,)); c.execute("INSERT INTO decisions VALUES(?,?,?)",(task,worker,fence)); c.commit(); c.close(); return True
def worker(name,prefix):
 while True:
  got=claim(name,prefix)
  if not got: return
  task,fence=got; time.sleep(.001); finish(name,task,fence)
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 if DB.exists(): raise FileExistsError("refusing to overwrite previous worker database")
 init()
 worker("solo","single")
 ts=[threading.Thread(target=worker,args=(f"w{i}","concurrent")) for i in range(3)]
 [t.start() for t in ts]; [t.join() for t in ts]
 old=claim("worker-old","stale")
 if old is None: raise AssertionError("stale fixture claim missing")
 c=conn(); c.execute("UPDATE tasks SET lease_until=0 WHERE id='stale-case'"); c.commit(); c.close()
 new=claim("worker-new","stale")
 stale_ok=finish("worker-old",old[0],old[1],record=False)
 new_ok=finish("worker-new",new[0],new[1])
 c=conn(); metrics={"single_done":c.execute("SELECT count(*) FROM tasks WHERE id LIKE 'single-%' AND status='done'").fetchone()[0],"concurrent_done":c.execute("SELECT count(*) FROM tasks WHERE id LIKE 'concurrent-%' AND status='done'").fetchone()[0],"single_duplicate_executions":c.execute("SELECT count(*) FROM (SELECT task,count(*) n FROM executions WHERE task LIKE 'single-%' GROUP BY task HAVING n>1)").fetchone()[0],"concurrent_duplicate_executions":c.execute("SELECT count(*) FROM (SELECT task,count(*) n FROM executions WHERE task LIKE 'concurrent-%' GROUP BY task HAVING n>1)").fetchone()[0],"decision_count":c.execute("SELECT count(*) FROM decisions").fetchone()[0],"decision_ownership_mismatches":c.execute("SELECT count(*) FROM decisions d JOIN tasks t ON d.task=t.id WHERE d.worker!=t.owner OR d.fence!=t.fence").fetchone()[0],"integrity":c.execute("PRAGMA integrity_check").fetchone()[0],"stale_fence":old[1],"new_fence":new[1],"stale_commit_accepted":stale_ok,"new_owner_commit_accepted":new_ok}; c.close()
 assert metrics["single_done"]==metrics["concurrent_done"]==100 and metrics["single_duplicate_executions"]==metrics["concurrent_duplicate_executions"]==0 and metrics["decision_ownership_mismatches"]==0 and not stale_ok and new_ok and metrics["integrity"]=="ok"
 (OUT/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n"); print(json.dumps(metrics,indent=2))
if __name__=="__main__":main()
