from __future__ import annotations
import hashlib,json,platform,sys
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];INPUT=BASE/"fixtures/inputs.json";RUN=BASE/"results/E025-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rows=[];mapping={"scale_service":"cpu","repair_database":"database","reroute_traffic":"network"}
    for c in json.loads(INPUT.read_text())["cases"]:
        ind=c["indicators"];scores={action:float(np.clip(.10+.75*ind[key]+.05*sum(ind[x] for x in ind if x!=key),0,1)) for action,key in mapping.items()}
        rows.append({"scenario_id":c["scenario_id"],"predicted_recovery":scores,"ranking":sorted(scores,key=lambda a:(-scores[a],a))})
    RUN.mkdir(parents=True,exist_ok=True);p=RUN/"predictions.json";p.write_text(json.dumps({"predictions":rows},indent=2)+"\n",encoding="utf-8")
    (RUN/"prediction-seal.json").write_text(json.dumps({"prediction_sha256":sha(p),"input_sha256":sha(INPUT),"labels_and_outcomes_loaded":False,"network_used":False,"device":"cpu","python":sys.version,"platform":platform.platform(),"numpy":np.__version__},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"predictions":len(rows),"actions":list(mapping),"labels_and_outcomes_loaded":False,"sealed":True},indent=2))
if __name__=="__main__":main()
