from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E021-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wilson(x,n):
    z=1.959963984540054;p=x/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d;return [float(c-h),float(c+h)]
def main():
    pf=RUN/"predictions.json";seal=json.loads((RUN/"prediction-seal.json").read_text())
    if seal["prediction_sha256"]!=sha(pf) or seal["labels_loaded"] is not False:raise SystemExit("seal invalid")
    rows=json.loads(pf.read_text())["predictions"];lp=BASE/"fixtures/evaluator-only/mechanism-labels.json";labels=json.loads(lp.read_text())["mechanisms"]
    if set(labels)!={r["scenario_id"] for r in rows}:raise SystemExit("label coverage mismatch")
    metrics={}
    for arm in ("observational_rule","intervention_rule"):
        tp=tn=fp=fn=0
        for r in rows:
            actual=labels[r["scenario_id"]]=="direct_cause";pred=r["predictions"][arm]
            if pred and actual:tp+=1
            elif pred and not actual:fp+=1
            elif not pred and not actual:tn+=1
            else:fn+=1
        sens=tp/(tp+fn);spec=tn/(tn+fp)
        metrics[arm]={"n":len(rows),"true_positive":tp,"false_positive":fp,"true_negative":tn,"false_negative":fn,"sensitivity":sens,"sensitivity_wilson95":wilson(tp,tp+fn),"specificity":spec,"specificity_wilson95":wilson(tn,tn+fp),"balanced_accuracy":(sens+spec)/2,"false_causal_rate_common_cause":fp/(fp+tn),"causal_detection_rate_direct_cause":tp/(tp+fn)}
    result={"experiment":"E021-R001","planning_stage":"XP018","dataset":"known synthetic structural mechanisms","metrics":metrics,"assumptions":["generated potential outcomes are valid matched interventions by construction","no unmeasured confounding for randomized within-context intervention contrast","observational correlation is not causal evidence"],"limitations":["simulation only","one specified linear mechanism family","paired potential outcomes are not jointly observed in real interventions"],"provenance":{"prediction_sha256":sha(pf),"input_sha256":sha(BASE/"fixtures/inputs.json"),"mechanism_label_sha256":sha(lp)},"interpretation":"Mechanism discrimination on the declared synthetic structural models only."}
    (RUN/"evaluation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
