import json,random
from pathlib import Path
ROOT=Path(__file__).resolve().parent; random.seed(37034)
def make(n,prefix,with_label):
 rows=[]; labels=[]
 for i in range(n):
  root=i%3; metrics=[]; topo=[]; temporal=[]
  for c in range(3):
   metrics.append(round(random.uniform(.70,.98) if c==root else random.uniform(.05,.70),4))
   topo.append(c==root or random.random()<.12); temporal.append(c==root or random.random()<.12)
  rows.append({"case_id":f"{prefix}-{i:04d}","features":metrics+list(map(int,topo))+list(map(int,temporal)),"evidence_ids":[f"{prefix}-{i:04d}-M{root}",f"{prefix}-{i:04d}-G{root}",f"{prefix}-{i:04d}-T{root}"]})
  labels.append(root)
 return rows,labels
tr,ty=make(300,"TR",True); te,ey=make(300,"TE",False)
(ROOT/"fixtures"/"train.json").write_text(json.dumps(tr,indent=2)+"\n"); (ROOT/"fixtures"/"test_inputs.json").write_text(json.dumps(te,indent=2)+"\n")
(ROOT/"evaluator"/"train_labels.json").write_text(json.dumps(ty)+"\n"); (ROOT/"evaluator"/"test_labels.json").write_text(json.dumps(ey)+"\n")
