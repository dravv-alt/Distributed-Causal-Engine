from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E024-R001"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pf=RUN/"predictions.json";seal=json.loads((RUN/"prediction-seal.json").read_text());assert sha(pf)==seal["prediction_sha256"] and not seal["labels_loaded"] and not seal["intervention_outcomes_loaded"]
    training=json.loads((BASE/"fixtures/training.json").read_text())["observations"];contexts=json.loads((BASE/"fixtures/heldout-inputs.json").read_text())["contexts"];oracle=json.loads((BASE/"fixtures/evaluator-only/intervention-outcomes.json").read_text())["outcomes"];rows=json.loads(pf.read_text())["predictions"];report=json.loads((RUN/"evaluation.json").read_text())
    a=np.array([x["a"] for x in training]);u=np.array([x["u"] for x in training]);y=np.array([x["y"] for x in training]);coef=np.linalg.lstsq(np.column_stack([np.ones(len(a)),a,u]),y,rcond=None)[0]
    by={x["context_id"]:x for x in contexts};errs=[];base=[];sq=[];bsq=[];sign=[];path=[]
    for r in rows:
        c=by[r["context_id"]];expected=float(coef[0]+coef[1]+coef[2]*c["u"]);assert abs(expected-r["predicted_y_do_1"])<1e-12
        truth=oracle[r["context_id"]]["y_do_1"];y0=c["observed_y_do_0"];effect=expected-y0;actual=truth-y0
        errs.append(abs(expected-truth));base.append(abs(y0-truth));sq.append((expected-truth)**2);bsq.append((y0-truth)**2);sign.append((effect>=0)==(actual>=0));path.append(effect>=.5)
    for key,val in (("mae",float(np.mean(errs))),("rmse",float(np.sqrt(np.mean(sq)))),("effect_direction_consistency",float(np.mean(sign))),("positive_path_accuracy_against_known_effect",float(np.mean(path)))):
        assert abs(val-report["counterfactual_prediction"][key])<1e-12
    assert abs(float(np.mean(base))-report["no_change_baseline"]["mae"])<1e-12 and abs(float(np.sqrt(np.mean(bsq)))-report["no_change_baseline"]["rmse"])<1e-12
    audit={"audit":"E024-R001 independent counterfactual audit","passed":True,"contexts":len(rows),"checks":["prediction seal and intervention label separation","training OLS independently refit","all 400 counterfactual predictions independently recomputed","prediction and no-change metrics independently recomputed"],"hashes":{"predictions":sha(pf),"training":sha(BASE/"fixtures/training.json"),"inputs":sha(BASE/"fixtures/heldout-inputs.json"),"oracle":sha(BASE/"fixtures/evaluator-only/intervention-outcomes.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8");print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
