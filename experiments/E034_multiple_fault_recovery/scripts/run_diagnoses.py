from __future__ import annotations
import hashlib,json
from pathlib import Path
BASE=Path(__file__).resolve().parents[1];INPUT=BASE/"fixtures/inputs.json";RUN=BASE/"results/E034-R001";A={"database":"repair_database","network":"reroute_traffic"}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    rows=[]
    for c in json.loads(INPUT.read_text())["cases"]:
        roots=sorted(k for k,v in c["signals"].items() if v>=.6);single=max(c["signals"],key=lambda k:(c["signals"][k],k))
        rows.append({"scenario_id":c["scenario_id"],"multi_root":{"roots":roots,"actions":[A[x] for x in roots]},"single_root_baseline":{"roots":[single],"actions":[A[single]]}})
    RUN.mkdir(parents=True,exist_ok=True);p=RUN/"diagnoses.json";p.write_text(json.dumps({"diagnoses":rows},indent=2)+"\n",encoding="utf-8")
    (RUN/"prediction-seal.json").write_text(json.dumps({"diagnoses_sha256":sha(p),"input_sha256":sha(INPUT),"root_schedule_loaded":False,"labels_loaded":False},indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"diagnoses":len(rows),"schedule_loaded":False,"sealed":True},indent=2))
if __name__=="__main__":main()
