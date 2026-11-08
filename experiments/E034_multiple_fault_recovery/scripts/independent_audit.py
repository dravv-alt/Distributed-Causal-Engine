from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];RUN=BASE/"results/E034-R001";FIX=BASE/"fixtures"
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    dp=RUN/"diagnoses.json";seal=json.loads((RUN/"prediction-seal.json").read_text());assert sha(dp)==seal["diagnoses_sha256"] and not seal["root_schedule_loaded"] and not seal["labels_loaded"]
    ds=json.loads(dp.read_text())["diagnoses"];out=json.loads((RUN/"sandbox-outcomes.json").read_text())["outcomes"];labels=json.loads((FIX/"evaluator-only/root-labels.json").read_text())["roots"];report=json.loads((RUN/"evaluation.json").read_text());ob={x["scenario_id"]:x for x in out};exact=mr=sr=joint=jm=js=inter=0
    for d in ds:
        sid=d["scenario_id"];roots=set(labels[sid]["root_set"]);assert set(d["multi_root"]["roots"])==roots
        expected={"database":"database" in roots,"network":"network" in roots};m=ob[sid];assert m["initial_state"]==expected
        for arm,actions in (("multi_root_final",d["multi_root"]["actions"]),("single_root_final",d["single_root_baseline"]["actions"])):
            state=dict(expected)
            for action in actions:state["database" if action=="repair_database" else "network"]=False
            assert state==m[arm]
        reversed_state=dict(expected)
        for action in reversed(d["multi_root"]["actions"]):reversed_state["database" if action=="repair_database" else "network"]=False
        assert reversed_state==m["multi_root_reverse_order_final"] and m["order_interference"]==(m["multi_root_final"]!=reversed_state)
        exact+=set(d["multi_root"]["roots"])==roots;mr+=not any(m["multi_root_final"].values());sr+=not any(m["single_root_final"].values());inter+=m["order_interference"]
        if len(roots)>1:joint+=1;jm+=not any(m["multi_root_final"].values());js+=not any(m["single_root_final"].values())
    n=len(ds);assert exact/n==report["multi_root_exact_set_accuracy"] and mr/n==report["multi_root_recovery_rate"] and sr/n==report["single_root_baseline_recovery_rate"] and jm/joint==report["joint_multi_root_recovery"] and js/joint==report["joint_single_root_baseline_recovery"] and inter==report["action_order_interference_cases"]
    audit={"audit":"E034-R001 independent root-set/recovery audit","passed":True,"cases":n,"checks":["label-blind prediction seal","root sets and action mappings recomputed","multi-root and single-root outcomes recomputed","both action orders checked for interference"],"hashes":{"diagnoses":sha(dp),"outcomes":sha(RUN/"sandbox-outcomes.json"),"labels":sha(FIX/"evaluator-only/root-labels.json"),"evaluation":sha(RUN/"evaluation.json")}}
    (RUN/"independent-audit.json").write_text(json.dumps(audit,indent=2)+"\n",encoding="utf-8");print(json.dumps(audit,indent=2))
if __name__=="__main__":main()
