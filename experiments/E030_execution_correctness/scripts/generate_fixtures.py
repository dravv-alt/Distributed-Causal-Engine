from __future__ import annotations
import json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures"
def main():
    rng=np.random.default_rng(30027);cases=[];actions=("restart","scale","reroute","rollback")
    for i in range(200):
        action=actions[i//50];replicas=int(rng.integers(2,6));healthy=int(rng.integers(1,replicas+1))
        state={"replicas":replicas,"healthy_replicas":healthy,"route":f"edge-{int(rng.integers(0,4))}","generation":int(rng.integers(0,20)),"last_action":"none"}
        args={}
        if action=="reroute":args={"target":f"edge-{int(rng.integers(4,8))}"}
        if action=="rollback":
            snapshot=dict(state);state["route"]="failed-target";state["generation"]+=1;state["last_action"]="uncommitted-change";args={"snapshot_state":snapshot}
        cases.append({"scenario_id":f"EXEC-{i:04d}","action":action,"initial_state":state,"arguments":args})
    FIX.mkdir(parents=True,exist_ok=True);(FIX/"inputs.json").write_text(json.dumps({"version":"synthetic-action-execution-v1","cases":cases},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(cases),"per_action":50,"seed":30027},indent=2))
if __name__=="__main__":main()
