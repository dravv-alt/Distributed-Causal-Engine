from __future__ import annotations
import hashlib,json
from pathlib import Path
import numpy as np
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E023-R001";METHODS=("observational","structural_adjusted","structural_omitted_u")
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def wilson(x,n):
    z=1.959963984540054;p=x/n;d=1+z*z/n;c=(p+z*z/(2*n))/d;h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n));return [float(max(0,c-h)),float(min(1,c+h))]
def main():
    pf=RUN/"predictions.json";seal=json.loads((RUN/"prediction-seal.json").read_text());assert sha(pf)==seal["prediction_sha256"] and not seal["labels_loaded"] and not seal["intervention_outcomes_loaded"]
    cases=json.loads((BASE/"fixtures/inputs.json").read_text())["cases"];rows=json.loads(pf.read_text())["predictions"];labels=json.loads((BASE/"fixtures/evaluator-only/mechanism-and-intervention-labels.json").read_text())["labels"];report=json.loads((RUN/"evaluation.json").read_text());by={c["scenario_id"]:c for c in cases}
    for row in rows:
        c=by[row["scenario_id"]];o=c["observations"];a=np.array([x["a"] for x in o]);u=np.array([x["u"] for x in o]);y=np.array([x["y"] for x in o]);simple=np.linalg.lstsq(np.column_stack([np.ones(len(a)),a]),y,rcond=None)[0][1];adjusted=np.linalg.lstsq(np.column_stack([np.ones(len(a)),a,u]),y,rcond=None)[0][1]
        assert abs(simple-row["observational_slope"])<1e-12 and abs(simple-row["structural_omitted_u_effect"])<1e-12 and abs(adjusted-row["structural_adjusted_effect"])<1e-12
        assert row["decisions"]["observational"]==(simple>=.5) and row["decisions"]["structural_adjusted"]==(adjusted>=.5)
    rec={}
    for method,key in (("observational","observational_slope"),("structural_adjusted","structural_adjusted_effect"),("structural_omitted_u","structural_omitted_u_effect")):
        tp=fp=tn=fn=0;err=[]
        for r in rows:
            lab=labels[r["scenario_id"]];actual=lab["mechanism"]=="direct_effect";pred=r["decisions"][method]
            tp+=pred and actual;fp+=pred and not actual;tn+=(not pred) and not actual;fn+=(not pred) and actual;err.append((r[key]-lab["intervention_effect"])**2)
        sens=tp/(tp+fn);spec=tn/(tn+fp);pc=tp+tn;rec[method]={"path_accuracy":pc/len(rows),"path_accuracy_wilson95":wilson(pc,len(rows)),"sensitivity":sens,"specificity":spec,"false_causal_rate_common_cause":fp/(fp+tn),"effect_rmse_vs_intervention_reference":float(np.sqrt(np.mean(err)))}
        for k,v in rec[method].items():
            pv=report["metrics"][method][k]
            if isinstance(v,list):assert np.allclose(v,pv,rtol=0,atol=1e-12)
            else:assert abs(v-pv)<1e-12
    audit={"audit":"E023-R001 independent structural-effect audit","passed":True,"cases":len(rows),"checks":["sealed predictions excluded labels and intervention outcomes","OLS estimates independently recomputed","decision thresholds and link accuracy recomputed","intervention-reference RMSE and confounder sensitivity recomputed"],"hashes":{"predictions":sha(pf),"inputs":sha(BASE/"fixtures/inputs.json"),"evaluator":sha(BASE/"fixtures/evaluator-only/mechanism-and-intervention-labels.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8");print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
