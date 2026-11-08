import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent; OUT=ROOT/"results"/"E038-R001"
pred=json.loads((OUT/"predictions.json").read_text()); labels=json.loads((ROOT/"evaluator"/"labels.json").read_text()); groups={}
for p,l in zip(pred,labels): groups.setdefault(l["class"],[]).append(p)
counts={k:{"cases":len(v),"accepted":sum(x["accepted"] for x in v),"abstained":sum(x["abstain"] for x in v)} for k,v in groups.items()}
result={"class_counts":counts,"unsupported_false_accepts":sum(x["accepted"] for x in groups["unsupported"]),"valid_retention":sum(x["accepted"] for x in groups["supported"])/len(groups["supported"]),"abstention_on_missing_modality":sum(x["abstain"] for x in groups["missing_modality"])/len(groups["missing_modality"]),"scope":"synthetic verifier fixture; proposals are not neural outputs"}
(OUT/"metrics.json").write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps(result,indent=2))
