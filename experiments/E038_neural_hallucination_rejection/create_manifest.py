import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent
files=["README.md","hypothesis.md","protocol.md","configuration.json","generate.py","run.py","evaluate.py","run.md","decision.md","fixtures/proposals.json","evaluator/labels.json","results/E038-R001/predictions.json","results/E038-R001/metrics.json"]
entries=[]
for rel in files:
 b=(root/rel).read_bytes(); entries.append({"path":rel,"bytes":len(b),"sha256":hashlib.sha256(b).hexdigest()})
(root/"results"/"E038-R001"/"artifact-manifest.json").write_text(json.dumps({"run":"E038-R001","files":entries,"scope":"synthetic verifier only"},indent=2)+"\n")
print(json.dumps({"hashed_files":len(entries)}))
