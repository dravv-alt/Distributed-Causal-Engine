from __future__ import annotations
import json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures"
MECH={"cpu_saturation":"cpu","database_saturation":"database","network_path_bottleneck":"network"}
def main():
    rng=np.random.default_rng(25022);kinds=["cpu_saturation"]*200+["database_saturation"]*200+["network_path_bottleneck"]*200;rng.shuffle(kinds);cases=[];labels={}
    actions={"cpu":"scale_service","database":"repair_database","network":"reroute_traffic"}
    for i,kind in enumerate(kinds):
        key=MECH[kind];ind={name:float(np.clip(rng.normal(.85 if name==key else .15,.18),0,1)) for name in ("cpu","database","network")}
        outcomes={}
        for candidate,action in actions.items():outcomes[action]=float(np.clip(rng.normal(.85 if candidate==key else .15,.08),0,1))
        sid=f"ACT-{i:04d}";cases.append({"scenario_id":sid,"indicators":ind});labels[sid]={"mechanism":kind,"controlled_recovery":outcomes}
    (FIX/"evaluator-only").mkdir(parents=True,exist_ok=True)
    (FIX/"inputs.json").write_text(json.dumps({"version":"synthetic-action-indicators-v1","cases":cases},indent=2)+"\n",encoding="utf-8")
    (FIX/"evaluator-only"/"mechanisms-and-outcomes.json").write_text(json.dumps({"cases":labels},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(cases),"mechanisms_balanced":True,"outcomes_separated":True,"seed":25022},indent=2))
if __name__=="__main__":main()
