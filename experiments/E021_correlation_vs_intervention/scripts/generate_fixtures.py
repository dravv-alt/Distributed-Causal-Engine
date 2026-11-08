from __future__ import annotations
import json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures"
def make(i,kind,rng):
    n=60;u=rng.normal(size=n)
    if kind=="direct_cause":
        a=rng.binomial(1,.5,size=n).astype(float); y=1.3*a+.7*u+rng.normal(0,.8,size=n)
    else:
        a=(u+rng.normal(0,.65,size=n)>0).astype(float); y=.95*u+rng.normal(0,.8,size=n)
    obs=[{"a":float(x),"y":float(z)} for x,z in zip(a,y)]
    contexts=[]
    u2=rng.normal(size=30)
    eps0=rng.normal(0,.45,size=30);eps1=rng.normal(0,.45,size=30)
    if kind=="direct_cause": y0=.7*u2+eps0;y1=1.3+.7*u2+eps1
    else: y0=.95*u2+eps0;y1=.95*u2+eps1
    for j in range(30): contexts.append({"context_id":f"C{j:02d}","y_do_0":float(y0[j]),"y_do_1":float(y1[j])})
    return {"scenario_id":f"MECH-{i:04d}","observations":obs,"matched_interventions":contexts}
def main():
    rng=np.random.default_rng(21018);cases=[];labels={}
    kinds=["direct_cause"]*300+["common_cause"]*300;rng.shuffle(kinds)
    for i,k in enumerate(kinds):cases.append(make(i,k,rng));labels[f"MECH-{i:04d}"]=k
    (FIX/"evaluator-only").mkdir(parents=True,exist_ok=True)
    (FIX/"inputs.json").write_text(json.dumps({"version":"synthetic_structural_mechanisms_v1","cases":cases},indent=2)+"\n",encoding="utf-8")
    (FIX/"evaluator-only"/"mechanism-labels.json").write_text(json.dumps({"mechanisms":labels},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(cases),"direct_cause":300,"common_cause":300,"labels_separated":True,"seed":21018},indent=2))
if __name__=="__main__":main()
