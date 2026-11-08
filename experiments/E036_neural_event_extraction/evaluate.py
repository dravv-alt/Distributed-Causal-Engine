import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent; OUT=ROOT/"results"/"E036-R001"
d=json.loads((ROOT/"evaluator"/"test_labels.json").read_text()); outputs=json.loads((OUT/"predictions.json").read_text())
n=[ ["connection_pool_exhaustion","timeout","healthy"].index(o["event_type"]) for o in outputs ]; y=d
texts=[r["text"].lower() for r in json.loads((ROOT/"fixtures"/"test_inputs.json").read_text())]
b=[0 if "pool" in t or "connection checkout" in t else 1 if "timeout" in t or "deadline" in t else 2 for t in texts]
def f1_macro(truth,pred):
 vals=[]
 for c in range(3):
  tp=sum(a==c and z==c for a,z in zip(truth,pred)); fp=sum(a!=c and z==c for a,z in zip(truth,pred)); fn=sum(a==c and z!=c for a,z in zip(truth,pred)); vals.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)
 return sum(vals)/3
schema=all(set(o)=={"event_type","service","timestamp","source_id","confidence"} and o["service"] and o["source_id"] for o in outputs)
result={"test_n":len(y),"neural_accuracy":sum(a==b for a,b in zip(y,n))/len(y),"neural_macro_f1":f1_macro(y,n),"keyword_accuracy":sum(a==b for a,b in zip(y,b))/len(y),"schema_compliant":schema,"provenance_retained":sum(bool(o["source_id"]) for o in outputs),"confidence_calibrated":False,"scope":"synthetic only; not RCAEval accuracy"}
(OUT/"metrics.json").write_text(json.dumps(result,indent=2)+"\n"); print(json.dumps(result,indent=2))
