import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent; OUT=ROOT/"results"/"E037-R001"
y=json.loads((ROOT/"evaluator"/"test_labels.json").read_text()); rows=json.loads((OUT/"predictions.json").read_text()); tr=json.loads((ROOT/"fixtures"/"test_inputs.json").read_text())
assert len(y)==len(rows)==len(tr)
correct=[r["candidate"]==z for r,z in zip(rows,y)]; accepted=[r for r in rows if r["accepted"]]
baseline=[max(range(3),key=lambda c:row["features"][c]) for row in tr]
metrics={"cases":len(y),"neural_top1_accuracy":sum(correct)/len(y),"metric_only_accuracy":sum(a==b for a,b in zip(baseline,y))/len(y),"accepted":len(accepted),"abstained":len(rows)-len(accepted),"accepted_candidate_utility":sum(r["candidate"]==z for r,z in zip(rows,y) if r["accepted"])/len(accepted) if accepted else None,"accepted_with_evidence_ids":sum(bool(r["evidence_ids"]) for r in accepted),"explanation_link_coverage":sum(bool(r["evidence_ids"]) for r in accepted)/len(accepted) if accepted else None,"label_use_in_inference":False,"scope":"synthetic only"}
(OUT/"metrics.json").write_text(json.dumps(metrics,indent=2)+"\n"); print(json.dumps(metrics,indent=2))
