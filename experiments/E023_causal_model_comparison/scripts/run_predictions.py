from __future__ import annotations
import hashlib,json,platform,sys
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];INPUT=BASE/"fixtures/inputs.json";RUN=BASE/"results/E023-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def estimate(c):
    obs=c["observations"];a=np.asarray([r["a"] for r in obs]);u=np.asarray([r["u"] for r in obs]);y=np.asarray([r["y"] for r in obs])
    obs_slope=float(np.linalg.lstsq(np.column_stack([np.ones(len(a)),a]),y,rcond=None)[0][1])
    adjusted=float(np.linalg.lstsq(np.column_stack([np.ones(len(a)),a,u]),y,rcond=None)[0][1])
    return {"observational_slope":obs_slope,"structural_adjusted_effect":adjusted,"structural_omitted_u_effect":obs_slope,"decisions":{"observational":obs_slope>=.5,"structural_adjusted":adjusted>=.5,"structural_omitted_u":obs_slope>=.5}}
def main():
    cases=json.loads(INPUT.read_text())["cases"];rows=[{"scenario_id":c["scenario_id"],**estimate(c)} for c in cases]
    RUN.mkdir(parents=True,exist_ok=True);p=RUN/"predictions.json";p.write_text(json.dumps({"predictions":rows},indent=2)+"\n",encoding="utf-8")
    (RUN/"prediction-seal.json").write_text(json.dumps({"prediction_sha256":sha(p),"input_sha256":sha(INPUT),"labels_loaded":False,"intervention_outcomes_loaded":False,"network_used":False,"device":"cpu","python":sys.version,"platform":platform.platform(),"numpy":np.__version__},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"predictions":len(rows),"models":["observational_slope","structural_adjusted","structural_omitted_u_sensitivity"],"labels_and_intervention_outcomes_loaded":False,"sealed":True},indent=2))
if __name__=="__main__":main()
