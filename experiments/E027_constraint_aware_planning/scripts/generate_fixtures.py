from __future__ import annotations
import json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures"
def main():
    rng=np.random.default_rng(27024);cases=[];labels={}
    for i in range(400):
        healthy=2+(i%3);budget=[1,4,7][int(rng.integers(0,3))];sid=f"SAFE-{i:04d}"
        cases.append({"scenario_id":sid,"healthy_replicas":healthy,"budget":budget,"goal":"restart_one"})
        feasible=(healthy>=3 and budget>=2) or (healthy==2 and budget>=7)
        labels[sid]={"feasible":feasible,"class":"feasible" if feasible else "infeasible"}
    (FIX/"evaluator-only").mkdir(parents=True,exist_ok=True)
    (FIX/"inputs.json").write_text(json.dumps({"version":"synthetic-safety-plans-v1","cases":cases},indent=2)+"\n",encoding="utf-8")
    (FIX/"evaluator-only"/"feasibility-labels.json").write_text(json.dumps({"cases":labels},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(cases),"labels_separated":True,"seed":27024},indent=2))
if __name__=="__main__":main()
