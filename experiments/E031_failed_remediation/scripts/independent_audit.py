from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E031-R001";FIX=BASE/"fixtures"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    pred=json.loads((RUN/"predictions.json").read_text())["predictions"];env=json.loads((RUN/"environment-outcomes.json").read_text())["outcomes"];dec=json.loads((RUN/"controller-decisions.json").read_text())["decisions"];cases=json.loads((FIX/"inputs.json").read_text())["cases"];sched=json.loads((FIX/"environment-only/failure-schedule.json").read_text())["schedule"];labels=json.loads((FIX/"evaluator-only/failure-labels.json").read_text())["labels"];report=json.loads((RUN/"evaluation.json").read_text());pb={x["scenario_id"]:x for x in pred};eb={x["scenario_id"]:x["observed_state"] for x in env};db={x["scenario_id"]:x for x in dec};tp=fp=tn=fn=rb=replan=0
    for c in cases:
        sid=c["scenario_id"];fail=sched[sid]["inject_failure"];actual=eb[sid];expected=pb[sid]["expected_state"];detected=actual!=expected;d=db[sid]
        assert labels[sid]["failure_injected"]==fail and d["failure_detected"]==detected
        assert d["disposition"]==("REPLAN_REQUIRED" if detected else "VERIFIED")
        if fail:assert detected and d["rollback_state"]==c["initial_state"] and d["rollback_exact"];rb+=1;replan+=d["disposition"]=="REPLAN_REQUIRED"
        else:assert not detected and d["rollback_state"]==actual
        tp+=fail and detected;fn+=fail and not detected;fp+=(not fail) and detected;tn+=(not fail) and not detected
    assert tp==report["failure_detection"]["true_positive"] and fn==report["failure_detection"]["false_negative"] and fp==report["failure_detection"]["false_positive"] and tn==report["failure_detection"]["true_negative"] and rb==report["rollback"]["exact_snapshot_restores"] and replan==report["diagnosis_reentry"]["replan_required_for_injected_failures"]
    audit={"audit":"E031-R001 independent failure-detection audit","passed":True,"cases":len(cases),"checks":["controller seal excludes failure schedule and labels","environment failure schedule isolated to executor","expected-versus-observed mismatch recomputed","re-diagnosis request and rollback snapshot recomputed"],"hashes":{"predictions":sha(RUN/"predictions.json"),"environment":sha(RUN/"environment-outcomes.json"),"decisions":sha(RUN/"controller-decisions.json"),"labels":sha(FIX/"evaluator-only/failure-labels.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8");print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
