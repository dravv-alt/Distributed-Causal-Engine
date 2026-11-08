from __future__ import annotations
import json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures";ACTIONS=("restart","scale","reroute")
def main():
    rng=np.random.default_rng(31028);cases=[];schedule={};labels={};i=0
    for action in ACTIONS:
        flags=[False]*40+[True]*40;rng.shuffle(flags)
        for failed in flags:
            sid=f"FAIL-{i:04d}";initial={"replicas":3,"healthy_replicas":3,"route":"edge-A","generation":int(rng.integers(0,20)),"last_action":"none"}
            args={"target":"edge-B"} if action=="reroute" else {}
            cases.append({"scenario_id":sid,"action":action,"initial_state":initial,"arguments":args});schedule[sid]={"inject_failure":failed};labels[sid]={"failure_injected":failed};i+=1
    (FIX/"environment-only").mkdir(parents=True,exist_ok=True);(FIX/"evaluator-only").mkdir(parents=True,exist_ok=True)
    (FIX/"inputs.json").write_text(json.dumps({"version":"simulated-failure-inputs-v1","cases":cases},indent=2)+"\n",encoding="utf-8")
    (FIX/"environment-only"/"failure-schedule.json").write_text(json.dumps({"schedule":schedule},indent=2)+"\n",encoding="utf-8")
    (FIX/"evaluator-only"/"failure-labels.json").write_text(json.dumps({"labels":labels},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(cases),"per_action":80,"failures":120,"successes":120,"inference_schedule_separated":True},indent=2))
if __name__=="__main__":main()
