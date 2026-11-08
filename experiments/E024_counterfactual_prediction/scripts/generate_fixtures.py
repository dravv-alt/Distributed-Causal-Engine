from __future__ import annotations
import json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures"
def main():
    rng=np.random.default_rng(24021)
    n=1000;u=rng.normal(size=n);a=rng.binomial(1,.5,size=n).astype(float);y=1.0*a+.8*u+rng.normal(0,.5,size=n)
    train=[{"a":float(x),"u":float(z),"y":float(v)} for x,z,v in zip(a,u,y)]
    contexts=[];oracle={}
    for i in range(400):
        z=float(rng.normal());y0=float(.8*z+rng.normal(0,.5));y1=float(1.0+.8*z+rng.normal(0,.5));sid=f"CF-{i:04d}"
        contexts.append({"context_id":sid,"u":z,"observed_y_do_0":y0});oracle[sid]={"y_do_1":y1,"true_effect":1.0}
    (FIX/"evaluator-only").mkdir(parents=True,exist_ok=True)
    (FIX/"training.json").write_text(json.dumps({"version":"synthetic-training-v1","observations":train},indent=2)+"\n",encoding="utf-8")
    (FIX/"heldout-inputs.json").write_text(json.dumps({"version":"synthetic-counterfactual-inputs-v1","contexts":contexts},indent=2)+"\n",encoding="utf-8")
    (FIX/"evaluator-only"/"intervention-outcomes.json").write_text(json.dumps({"outcomes":oracle},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"training_observations":len(train),"heldout_contexts":len(contexts),"intervention_labels_separated":True},indent=2))
if __name__=="__main__":main()
