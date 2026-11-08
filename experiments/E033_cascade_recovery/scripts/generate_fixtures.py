from __future__ import annotations
import json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures"
def main():
    rng=np.random.default_rng(33030);cases=[];labels={};nodes=("database","service_b","service_a","retry_queue");edges=[[nodes[i],nodes[i+1]] for i in range(3)]
    for i in range(300):
        onsets=[float(j+rng.normal(0,.3)) for j in range(4)];cases.append({"scenario_id":f"CAS-{i:04d}","symptoms":{n:True for n in nodes},"onset":{n:onsets[j] for j,n in enumerate(nodes)},"causal_edges":edges});labels[f"CAS-{i:04d}"]={"root":"database","propagation_path":list(nodes)}
    (FIX/"evaluator-only").mkdir(parents=True,exist_ok=True)
    (FIX/"inputs.json").write_text(json.dumps({"version":"synthetic-db-cascade-v1","cases":cases},indent=2)+"\n",encoding="utf-8")
    (FIX/"evaluator-only/root-labels.json").write_text(json.dumps({"labels":labels},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(cases),"causal_edges":3,"labels_separated":True,"seed":33030},indent=2))
if __name__=="__main__":main()
