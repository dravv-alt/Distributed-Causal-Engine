from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E023-R001";METHODS=("observational","structural_adjusted","structural_omitted_u")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wilson(x,n):
    z=1.959963984540054;p=x/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n));return [float(max(0,c-h)),float(min(1,c+h))]
def main():
    pf=RUN/"predictions.json";seal=json.loads((RUN/"prediction-seal.json").read_text())
    if seal["prediction_sha256"]!=sha(pf) or seal["labels_loaded"] is not False or seal["intervention_outcomes_loaded"] is not False:raise SystemExit("prediction seal invalid")
    rows=json.loads(pf.read_text())["predictions"];lp=BASE/"fixtures/evaluator-only/mechanism-and-intervention-labels.json";labels=json.loads(lp.read_text())["labels"]
    if set(labels)!={r["scenario_id"] for r in rows}:raise SystemExit("label coverage mismatch")
    metrics={}
    for method in METHODS:
        estimate_key={"observational":"observational_slope","structural_adjusted":"structural_adjusted_effect","structural_omitted_u":"structural_omitted_u_effect"}[method]
        tp=fp=tn=fn=0;errors=[]
        for row in rows:
            label=labels[row["scenario_id"]];pred=row["decisions"][method];actual=label["mechanism"]=="direct_effect"
            tp+=pred and actual;fp+=pred and not actual;tn+=(not pred) and not actual;fn+=(not pred) and actual
            errors.append((row[estimate_key]-label["intervention_effect"])**2)
        sens=tp/(tp+fn);spec=tn/(tn+fp)
        path_correct=tp+tn
        metrics[method]={"n":len(rows),"path_accuracy":path_correct/len(rows),"path_accuracy_wilson95":wilson(path_correct,len(rows)),"sensitivity":sens,"sensitivity_wilson95":wilson(tp,tp+fn),"specificity":spec,"specificity_wilson95":wilson(tn,tn+fp),"false_causal_rate_common_cause":fp/(fp+tn),"effect_rmse_vs_intervention_reference":float(np.sqrt(np.mean(errors)))}
    changed=sum(r["decisions"]["structural_adjusted"]!=r["decisions"]["structural_omitted_u"] for r in rows)
    sensitivity=float(np.mean([abs(r["structural_adjusted_effect"]-r["structural_omitted_u_effect"]) for r in rows]))
    result={"experiment":"E023-R001","planning_stage":"XP020","dataset":"synthetic measured-confounder SCMs","metrics":metrics,"assumption_sensitivity":{"mean_absolute_effect_change_when_U_omitted":sensitivity,"link_decision_changed_cases":changed,"n_cases":len(rows),"assumption":"U measured and included in adjusted model"},"provenance":{"prediction_sha256":sha(pf),"input_sha256":sha(BASE/"fixtures/inputs.json"),"evaluator_label_and_intervention_sha256":sha(lp)},"interpretation":"Synthetic structural-model comparison only; no real causal identification claim."}
    (RUN/"evaluation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
