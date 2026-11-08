import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent; OUT=ROOT/"results"/"E038-R001"
rows=json.loads((ROOT/"fixtures"/"proposals.json").read_text()); out=[]
for row in rows:
 f=row["features"]; accepted=f["metric"]>=.55 and f["topology"] and f["temporal"]
 out.append({"case_id":row["case_id"],"accepted":accepted,"abstain":not accepted,"evidence_ids":row["evidence_ids"] if accepted else []})
OUT.mkdir(parents=True,exist_ok=True); (OUT/"predictions.json").write_text(json.dumps(out,indent=2)+"\n")
print(json.dumps({"predictions":len(out),"labels_loaded":False}))
