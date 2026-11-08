import json,torch
from pathlib import Path
from torch import nn
ROOT=Path(__file__).resolve().parent; OUT=ROOT/"results"/"E037-R001"
def main():
 torch.manual_seed(37034); torch.set_num_threads(1)
 tr=json.loads((ROOT/"fixtures"/"train.json").read_text()); te=json.loads((ROOT/"fixtures"/"test_inputs.json").read_text()); y=json.loads((ROOT/"evaluator"/"train_labels.json").read_text())
 x=torch.tensor([r["features"] for r in tr],dtype=torch.float32); target=torch.tensor(y)
 model=nn.Linear(9,3); opt=torch.optim.Adam(model.parameters(),lr=.04)
 for _ in range(200):
  opt.zero_grad(); loss=nn.functional.cross_entropy(model(x),target); loss.backward(); opt.step()
 tx=torch.tensor([r["features"] for r in te],dtype=torch.float32)
 with torch.no_grad(): pred=model(tx).argmax(1).tolist()
 out=[]
 for row,cand in zip(te,pred):
  f=row["features"]; accepted=f[cand]>=.55 and f[3+cand]==1 and f[6+cand]==1
  out.append({"case_id":row["case_id"],"candidate":cand,"accepted":accepted,"abstain":not accepted,"evidence_ids":row["evidence_ids"] if accepted else []})
 OUT.mkdir(parents=True,exist_ok=True); (OUT/"predictions.json").write_text(json.dumps(out,indent=2)+"\n")
 print(json.dumps({"train":len(tr),"test":len(te),"test_labels_loaded":False}))
if __name__=="__main__":main()
