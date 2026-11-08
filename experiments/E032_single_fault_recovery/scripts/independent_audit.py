from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E032-R001";FIX=BASE/"fixtures";ACT={"cpu":"scale_service","database":"repair_database","network":"reroute_traffic"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    dp=RUN/"controller-decisions.json";seal=json.loads((RUN/"controller-seal.json").read_text());assert sha(dp)==seal["decisions_sha256"] and not seal["fault_schedule_loaded"] and not seal["fault_labels_loaded"]
    decisions=json.loads(dp.read_text())["decisions"];cases=json.loads((FIX/"inputs.json").read_text())["cases"];outcomes=json.loads((RUN/"sandbox-outcomes.json").read_text())["outcomes"];labels=json.loads((FIX/"evaluator-only/fault-labels.json").read_text())["faults"];report=json.loads((RUN/"evaluation.json").read_text());cb={c["scenario_id"]:c for c in cases};ob={x["scenario_id"]:x for x in outcomes};correct=recovered=false=approved=denied=0
    for d in decisions:
        c=cb[d["scenario_id"]];diagnosis=max(c["signals"],key=lambda k:(c["signals"][k],k));assert diagnosis==d["diagnosis"] and d["action"]==ACT[diagnosis] and d["plan_valid"]
        true=labels[d["scenario_id"]]["true_fault"];action=d["approved"] and diagnosis==true;actual=ob[d["scenario_id"]]
        assert actual["recovered"]==action and actual["false_remediation"]==(d["approved"] and diagnosis!=true)
        correct+=diagnosis==true;recovered+=action;false+=actual["false_remediation"];approved+=d["approved"];denied+=not d["approved"]
    assert report["diagnosis_accuracy"]==correct/len(decisions) and report["recovery"]["successful"]==recovered and report["false_remediation"]["count"]==false and report["simulated_approval"]["approved"]==approved and report["simulated_approval"]["declined_without_approval"]==denied
    audit={"audit":"E032-R001 independent closed-loop simulation audit","passed":True,"cases":len(decisions),"checks":["controller schedule/label isolation","diagnosis and action map independently recomputed","approval-gated simulator execution recomputed","recovery and false-remediation metrics recomputed"],"hashes":{"decisions":sha(dp),"outcomes":sha(RUN/"sandbox-outcomes.json"),"labels":sha(FIX/"evaluator-only/fault-labels.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8");print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
