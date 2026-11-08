from __future__ import annotations
import json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures";MECH=("cpu","database","network")
def main():
    rng=np.random.default_rng(32029);cases=[];labels={};schedule={};items=[m for m in MECH for _ in range(100)];rng.shuffle(items)
    for i,m in enumerate(items):
        signals={k:float(rng.normal(1.0 if k==m else .45,.7)) for k in MECH};approved=bool(rng.random()<.8);sid=f"SF-{i:04d}"
        cases.append({"scenario_id":sid,"signals":signals,"simulated_operator_approval":approved});labels[sid]={"true_fault":m};schedule[sid]={"true_fault":m}
    (FIX/"environment-only").mkdir(parents=True,exist_ok=True);(FIX/"evaluator-only").mkdir(parents=True,exist_ok=True)
    (FIX/"inputs.json").write_text(json.dumps({"version":"synthetic-single-fault-v1","cases":cases},indent=2)+"\n",encoding="utf-8")
    (FIX/"environment-only/fault-schedule.json").write_text(json.dumps({"faults":schedule},indent=2)+"\n",encoding="utf-8")
    (FIX/"evaluator-only/fault-labels.json").write_text(json.dumps({"faults":labels},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(cases),"balanced_fault_types":True,"simulated_approvals":sum(x["simulated_operator_approval"] for x in cases),"labels_separated":True},indent=2))
if __name__=="__main__":main()
