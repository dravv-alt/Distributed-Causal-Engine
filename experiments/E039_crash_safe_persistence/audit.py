import json,sqlite3
from pathlib import Path
root=Path(__file__).resolve().parent; db=root/"results"/"E039-R001"/"crash-lab.sqlite"
c=sqlite3.connect(db)
res={"integrity":c.execute("PRAGMA integrity_check").fetchone()[0],"inputs":c.execute("SELECT count(*) FROM inputs").fetchone()[0],"decisions":c.execute("SELECT count(*) FROM decisions").fetchone()[0],"decision_duplicates":c.execute("SELECT count(*)-count(DISTINCT id) FROM decisions").fetchone()[0],"deliveries":c.execute("SELECT count(*) FROM deliveries").fetchone()[0],"delivery_duplicates":c.execute("SELECT count(*)-count(DISTINCT id) FROM deliveries").fetchone()[0],"unsent_outbox":c.execute("SELECT count(*) FROM outbox WHERE sent=0").fetchone()[0]}
c.close(); assert res=={"integrity":"ok","inputs":72,"decisions":72,"decision_duplicates":0,"deliveries":72,"delivery_duplicates":0,"unsent_outbox":0}
(root/"results"/"E039-R001"/"independent-audit.json").write_text(json.dumps(res,indent=2)+"\n"); print(json.dumps(res,indent=2))
