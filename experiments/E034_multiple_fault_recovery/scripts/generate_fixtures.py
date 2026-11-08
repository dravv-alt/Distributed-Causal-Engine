from __future__ import annotations
import json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures"
def main():
    rng=np.random.default_rng(34031);groups=[["database"]]*100+[["network"]]*100+[["database","network"]]*100;rng.shuffle(groups);cases=[];labels={}
    for i,roots in enumerate(groups):
        signals={k:float(rng.normal(.9 if k in roots else .1,.1)) for k in ("database","network")};sid=f"MF-{i:04d}";cases.append({"scenario_id":sid,"signals":signals});labels[sid]={"root_set":sorted(roots)}
    (FIX/"environment-only").mkdir(parents=True,exist_ok=True);(FIX/"evaluator-only").mkdir(parents=True,exist_ok=True)
    (FIX/"inputs.json").write_text(json.dumps({"version":"synthetic-multiple-fault-v1","cases":cases},indent=2)+"\n",encoding="utf-8")
    (FIX/"environment-only/root-schedule.json").write_text(json.dumps({"roots":labels},indent=2)+"\n",encoding="utf-8")
    (FIX/"evaluator-only/root-labels.json").write_text(json.dumps({"roots":labels},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(cases),"groups":{"db_only":100,"network_only":100,"joint":100},"labels_separated":True},indent=2))
if __name__=="__main__":main()
