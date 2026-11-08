import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
cases=[]; labels=[]
for group in ["supported","unsupported","missing_modality"]:
 for i in range(100):
  idx=len(cases); features={"metric":.9 if group!="unsupported" else .1,"topology":group=="supported","temporal":group=="supported"}
  if group=="missing_modality": features["topology"]=True; features["temporal"]=False
  cases.append({"case_id":f"H{idx+1:03d}","candidate":"db_overload","features":features,"evidence_ids":[f"EV-{idx+1:03d}-M",f"EV-{idx+1:03d}-G",f"EV-{idx+1:03d}-T"]})
  labels.append({"case_id":f"H{idx+1:03d}","class":group})
(ROOT/"fixtures"/"proposals.json").write_text(json.dumps(cases,indent=2)+"\n")
(ROOT/"evaluator"/"labels.json").write_text(json.dumps(labels,indent=2)+"\n")
