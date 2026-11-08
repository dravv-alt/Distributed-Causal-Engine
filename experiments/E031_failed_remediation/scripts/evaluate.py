from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E031-R001";FIX=BASE/"fixtures"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    decisionp=RUN/"controller-decisions.json";seal=json.loads((RUN/"controller-seal.json").read_text())
    if seal["decisions_sha256"]!=sha(decisionp) or seal["failure_schedule_loaded"] is not False:raise SystemExit("controller seal invalid")
    rows=json.loads(decisionp.read_text())["decisions"];labels=json.loads((FIX/"evaluator-only/failure-labels.json").read_text())["labels"];tp=fp=tn=fn=rollback=replan=0;per={a:{"n":0,"failures_detected":0} for a in ("restart","scale","reroute")};cases=json.loads((FIX/"inputs.json").read_text())["cases"];by={x["scenario_id"]:x for x in cases}
    for r in rows:
        actual=labels[r["scenario_id"]]["failure_injected"];pred=r["failure_detected"];tp+=actual and pred;fp+=(not actual) and pred;tn+=(not actual) and not pred;fn+=actual and not pred;rollback+=actual and r["rollback_exact"];replan+=actual and r["disposition"]=="REPLAN_REQUIRED";a=by[r["scenario_id"]]["action"];per[a]["n"]+=1;per[a]["failures_detected"]+=actual and pred
    result={"experiment":"E031-R001","planning_stage":"XP028","cases":len(rows),"failure_detection":{"true_positive":tp,"false_positive":fp,"true_negative":tn,"false_negative":fn,"sensitivity":tp/(tp+fn) if tp+fn else None,"false_alarm_rate":fp/(fp+tn) if fp+tn else None},"diagnosis_reentry":{"replan_required_for_injected_failures":replan,"injected_failures":tp+fn},"rollback":{"exact_snapshot_restores":rollback,"injected_failures":tp+fn,"external_rollback_executed":False},"per_action":per,"environment_schedule_visible_to_controller":False,"provenance":{"predictions_sha256":sha(RUN/"predictions.json"),"environment_outcomes_sha256":sha(RUN/"environment-outcomes.json"),"decisions_sha256":sha(decisionp),"failure_label_sha256":sha(FIX/"evaluator-only/failure-labels.json")},"interpretation":"Synthetic failure-injection and rollback-state simulation only."}
    (RUN/"evaluation.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8");print(json.dumps(result,indent=2))
if __name__=="__main__":main()
