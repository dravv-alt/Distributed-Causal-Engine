import json,sqlite3
from pathlib import Path
root=Path(__file__).resolve().parent; c=sqlite3.connect(root/"results"/"E040-R001"/"workers.sqlite")
r={"integrity":c.execute("PRAGMA integrity_check").fetchone()[0],"done":c.execute("SELECT count(*) FROM tasks WHERE status='done'").fetchone()[0],"executions":c.execute("SELECT count(*) FROM executions").fetchone()[0],"duplicate_tasks":c.execute("SELECT count(*) FROM (SELECT task,count(*) n FROM executions GROUP BY task HAVING n>1)").fetchone()[0],"ownership_mismatches":c.execute("SELECT count(*) FROM decisions d JOIN tasks t ON d.task=t.id WHERE d.worker!=t.owner OR d.fence!=t.fence").fetchone()[0]}; c.close()
assert r=={"integrity":"ok","done":201,"executions":201,"duplicate_tasks":0,"ownership_mismatches":0}
(root/"results"/"E040-R001"/"independent-audit.json").write_text(json.dumps(r,indent=2)+"\n"); print(json.dumps(r,indent=2))
