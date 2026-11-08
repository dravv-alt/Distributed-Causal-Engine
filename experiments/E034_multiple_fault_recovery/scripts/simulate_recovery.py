from __future__ import annotations
import json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];FIX=BASE/"fixtures";RUN=BASE/"results/E034-R001";ROOT_FOR={"repair_database":"database","reroute_traffic":"network"}
def apply(initial,actions):
    state=dict(initial)
    for action in actions:state[ROOT_FOR[action]]=False
    return state
def main():
    diagnoses=json.loads((RUN/"diagnoses.json").read_text())["diagnoses"];schedule=json.loads((FIX/"environment-only/root-schedule.json").read_text())["roots"];rows=[]
    for d in diagnoses:
        actual=set(schedule[d["scenario_id"]]["root_set"]);initial={"database":"database" in actual,"network":"network" in actual}
        multi=d["multi_root"]["actions"];single=d["single_root_baseline"]["actions"];fwd=apply(initial,multi);rev=apply(initial,list(reversed(multi)));base=apply(initial,single)
        rows.append({"scenario_id":d["scenario_id"],"initial_state":initial,"multi_root_final":fwd,"multi_root_reverse_order_final":rev,"single_root_final":base,"order_interference":fwd!=rev})
    (RUN/"sandbox-outcomes.json").write_text(json.dumps({"outcomes":rows},indent=2)+"\n",encoding="utf-8");print(json.dumps({"cases":len(rows),"external_actions":False,"simulated":True},indent=2))
if __name__=="__main__":main()
