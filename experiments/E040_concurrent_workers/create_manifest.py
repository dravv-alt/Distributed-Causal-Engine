import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent; rels=["README.md","hypothesis.md","protocol.md","configuration.json","run.py","audit.py","run.md","decision.md","results/E040-R001/metrics.json","results/E040-R001/independent-audit.json"]
entries=[]
for rel in rels:
 b=(root/rel).read_bytes(); entries.append({"path":rel,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()})
db=root/"results"/"E040-R001"/"workers.sqlite"; entries.append({"path":"results/E040-R001/workers.sqlite","bytes":db.stat().st_size,"sha256":hashlib.sha256(db.read_bytes()).hexdigest()})
(root/"results"/"E040-R001"/"artifact-manifest.json").write_text(json.dumps({"run":"E040-R001","files":entries,"scope":"SQLite/thread simulator"},indent=2)+"\n"); print(json.dumps({"hashed_files":len(entries)}))
