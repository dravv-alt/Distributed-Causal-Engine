from __future__ import annotations
import hashlib,json,platform,sys
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];INPUT=BASE/"fixtures/inputs.json";RUN=BASE/"results/E021-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    cases=json.loads(INPUT.read_text())["cases"];outrows=[]
    for c in cases:
        a=np.asarray([r["a"] for r in c["observations"]]);y=np.asarray([r["y"] for r in c["observations"]]);corr=float(np.corrcoef(a,y)[0,1])
        effect=float(np.mean([x["y_do_1"]-x["y_do_0"] for x in c["matched_interventions"]]))
        outrows.append({"scenario_id":c["scenario_id"],"observational_correlation":corr,"intervention_effect_estimate":effect,"predictions":{"observational_rule":abs(corr)>=.5,"intervention_rule":effect>=.5}})
    RUN.mkdir(parents=True,exist_ok=True);p=RUN/"predictions.json";p.write_text(json.dumps({"predictions":outrows},indent=2)+"\n",encoding="utf-8")
    (RUN/"prediction-seal.json").write_text(json.dumps({"prediction_sha256":sha(p),"input_sha256":sha(INPUT),"labels_loaded":False,"network_used":False,"device":"cpu","python":sys.version,"platform":platform.platform(),"numpy":np.__version__},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"predictions":len(outrows),"arms":["observational_rule","intervention_rule"],"labels_loaded":False,"sealed":True},indent=2))
if __name__=="__main__":main()
