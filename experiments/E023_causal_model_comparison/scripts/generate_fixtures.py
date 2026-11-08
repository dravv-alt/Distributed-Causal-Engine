from __future__ import annotations
import json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures"
def main():
    rng=np.random.default_rng(22020);cases=[];labels={}
    kinds=["direct_effect"]*300+["common_cause_no_effect"]*300;rng.shuffle(kinds)
    for i,kind in enumerate(kinds):
        n=100;u=rng.normal(size=n)
        if kind=="direct_effect":a=rng.normal(size=n);y=1.2*a+.8*u+rng.normal(0,.7,size=n);true=1.2
        else:a=u+rng.normal(0,.55,size=n);y=1.0*u+rng.normal(0,.7,size=n);true=0.0
        obs=[{"a":float(x),"u":float(z),"y":float(v)} for x,z,v in zip(a,u,y)]
        ui=rng.normal(size=40);eps0=rng.normal(0,.35,size=40);eps1=rng.normal(0,.35,size=40)
        if kind=="direct_effect":y0=.8*ui+eps0;y1=1.2+.8*ui+eps1
        else:y0=1.0*ui+eps0;y1=1.0*ui+eps1
        interventions=[{"context_id":f"I{j:02d}","y_do_0":float(y0[j]),"y_do_1":float(y1[j])} for j in range(40)]
        sid=f"SCM-{i:04d}";cases.append({"scenario_id":sid,"observations":obs});labels[sid]={"mechanism":kind,"true_effect":true,"intervention_effect":float(np.mean(y1-y0))}
    (FIX/"evaluator-only").mkdir(parents=True,exist_ok=True)
    (FIX/"inputs.json").write_text(json.dumps({"version":"synthetic-linear-structural-v1","cases":cases},indent=2)+"\n",encoding="utf-8")
    (FIX/"evaluator-only"/"mechanism-and-intervention-labels.json").write_text(json.dumps({"labels":labels},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(cases),"labels_separated":True,"seed":22020},indent=2))
if __name__=="__main__":main()
