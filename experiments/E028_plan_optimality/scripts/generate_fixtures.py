from __future__ import annotations
import json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures"
def main():
    rng=np.random.default_rng(28025);cases=[]
    for i in range(400):cases.append({"scenario_id":f"OBJ-{i:04d}","healthy_replicas":2+int(rng.integers(0,3)),"budget":[1,2,4,7][int(rng.integers(0,4))]})
    FIX.mkdir(parents=True,exist_ok=True);(FIX/"inputs.json").write_text(json.dumps({"version":"synthetic-objective-cases-v1","cases":cases},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"cases":len(cases),"seed":28025},indent=2))
if __name__=="__main__":main()
