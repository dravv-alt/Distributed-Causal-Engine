from __future__ import annotations
import hashlib,json,platform,sys
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E024-R001";INPUT=BASE/"fixtures/heldout-inputs.json";MODEL=RUN/"model.json"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    model=json.loads(MODEL.read_text());b0,b1,b2=model["coefficients"];contexts=json.loads(INPUT.read_text())["contexts"];rows=[]
    for c in contexts:
        predicted=float(b0+b1*1.0+b2*c["u"]);rows.append({"context_id":c["context_id"],"observed_y_do_0":c["observed_y_do_0"],"predicted_y_do_1":predicted,"predicted_effect":predicted-c["observed_y_do_0"]})
    p=RUN/"predictions.json";p.write_text(json.dumps({"predictions":rows},indent=2)+"\n",encoding="utf-8")
    seal={"prediction_sha256":sha(p),"input_sha256":sha(INPUT),"model_sha256":sha(MODEL),"training_sha256":model["training_sha256"],"labels_loaded":False,"intervention_outcomes_loaded":False,"network_used":False,"device":"cpu","python":sys.version,"platform":platform.platform(),"numpy":np.__version__}
    (RUN/"prediction-seal.json").write_text(json.dumps(seal,indent=2)+"\n",encoding="utf-8");print(json.dumps({"predictions":len(rows),"labels_loaded":False,"sealed":True,"estimated_a_coefficient":b1},indent=2))
if __name__=="__main__":main()
