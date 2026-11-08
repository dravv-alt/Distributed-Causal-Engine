from __future__ import annotations
import json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures";ACTIONS={"database_saturated":120,"service_overloaded":100,"network_congested":80}
def main():
    rng=np.random.default_rng(26023);cases=[];labels={}
    for i in range(400):
        if i<100:
            latency=float(rng.uniform(20,100));flags={k:bool(rng.integers(0,2)) for k in ACTIONS}
        elif i<300:
            flags={k:False for k in ACTIONS}
            selected=list(ACTIONS);rng.shuffle(selected)
            for key in selected[:int(rng.integers(1,4))]:flags[key]=True
            capacity=sum(ACTIONS[k] for k,v in flags.items() if v)
            latency=float(rng.uniform(101,min(500,capacity+100))) if capacity>1 else 101.0
        else:
            latency=float(rng.uniform(101,400));flags={k:False for k in ACTIONS}
        sid=f"PLAN-{i:04d}";cases.append({"scenario_id":sid,"state":{"latency_ms":latency,**flags},"goal":{"latency_at_most_ms":100}})
        possible=latency<=100 or latency-sum(ACTIONS[k] for k,v in flags.items() if v)<=100
        labels[sid]={"reachable":possible,"class":"already_satisfied" if latency<=100 else "reachable" if possible else "unreachable"}
    (FIX/"evaluator-only").mkdir(parents=True,exist_ok=True)
    (FIX/"inputs.json").write_text(json.dumps({"version":"synthetic-planning-v1","cases":cases},indent=2)+"\n",encoding="utf-8")
    (FIX/"evaluator-only"/"reachability-labels.json").write_text(json.dumps({"cases":labels},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(cases),"labels_separated":True,"already_satisfied":sum(v["class"]=="already_satisfied" for v in labels.values()),"reachable":sum(v["class"]=="reachable" for v in labels.values()),"unreachable":sum(v["class"]=="unreachable" for v in labels.values())},indent=2))
if __name__=="__main__":main()
