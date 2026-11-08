import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent
files=["README.md","hypothesis.md","protocol.md","configuration.json","run.py","audit.py","run.md","decision.md","results/E039-R001/trials.json","results/E039-R001/metrics.json","results/E039-R001/independent-audit.json"]
entries=[]
for rel in files:
 b=(root/rel).read_bytes(); entries.append({"path":rel,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()})
db=root/"results"/"E039-R001"/"crash-lab.sqlite"; entries.append({"path":"results/E039-R001/crash-lab.sqlite","bytes":db.stat().st_size,"sha256":hashlib.sha256(db.read_bytes()).hexdigest()})
(root/"results"/"E039-R001"/"artifact-manifest.json").write_text(json.dumps({"run":"E039-R001","files":entries,"scope":"isolated SQLite simulator"},indent=2)+"\n")
print(json.dumps({"hashed_files":len(entries)}))
