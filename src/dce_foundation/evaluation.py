"""E003 experiment harness, not an RCA evaluator."""
import argparse
from datetime import datetime, timezone
from dataclasses import asdict
import gc
from pathlib import Path
import platform
import subprocess
import sys
import networkx as nx
from .domain import canonical_json,digest
from .event_time import normalize_time
from .inspection import inspect_dataset,file_hash
from .replay.openrca import replay
from .telemetry.openrca import SCENARIOS,OpenRCAAdapter


def run(root, output, cap=2000):
    output=Path(output)
    output.mkdir(parents=True,exist_ok=False)
    adapter=OpenRCAAdapter(root)
    result=[]
    for scenario in SCENARIOS:
        records=sorted(adapter.labels(scenario),key=lambda p:(normalize_time(p[1]["timestamp"],"timestamp","s").epoch_ns,p[0]))
        for line,row in (records[0],records[-1]):
            iid=f"{scenario}@{line}"
            incident,graph,report=replay(root,iid,cap)
            # Small independent serialization sample for review, excluding label text.
            sample={"incident":iid,"observations":[asdict(o) for o in incident.observations[:3]],
                    "dependencies":[asdict(d) for d in incident.dependencies[:3]]}
            (output/(iid.replace("/","_")+"-sample.json")).write_text(canonical_json(sample)+"\n",encoding="utf-8")
            report_digest=digest(report)
            del incident,graph
            gc.collect()
            repeated,graph2,report2=replay(root,iid,cap)
            report["deterministic_repeat"]=report_digest==digest(report2)
            result.append(report)
            print(iid,report["observations"],report["schema"],"repeat",report["deterministic_repeat"],flush=True)
            del repeated,graph2,report2
            gc.collect()
    summary={"experiment":"E003","run":"E003-R001","scope":"bounded cross-system adequacy; not full release audit",
             "reports":result,"all_deterministic":all(r["deterministic_repeat"] for r in result),
             "downstream_ready":all(r["downstream_ready"] for r in result),"review_required":True}
    (output/"adequacy.json").write_text(canonical_json(summary)+"\n",encoding="utf-8")
    source_paths=sorted(Path("src/dce_foundation").rglob("*.py"))+sorted(Path("tests").rglob("*.py"))
    source_paths += [Path("pyproject.toml"),Path("experiments/E003_domain_model_adequacy/protocol.md"),Path("experiments/E003_domain_model_adequacy/configuration.yaml")]
    git_head=subprocess.run(["git","rev-parse","HEAD"],capture_output=True,text=True).stdout.strip()
    dirty=subprocess.run(["git","status","--porcelain"],capture_output=True,text=True).stdout.splitlines()
    manifest={"run":"E003-R001","executed_at_utc":datetime.now(timezone.utc).isoformat(),
              "command":sys.argv,"max_rows_per_file":cap,"python":sys.version,"networkx":nx.__version__,
              "hardware":{"platform":platform.platform(),"machine":platform.machine(),"processor":platform.processor()},
              "git_head":git_head,"dirty_status":dirty,"source_hashes":{p.as_posix():file_hash(p) for p in source_paths},
              "source_snapshot":"source-snapshot.zip","dataset_manifest_sha256":file_hash("data/manifests/openrca.json"),
              "result_sha256":file_hash(output/"adequacy.json"),"random_seed":None}
    import zipfile
    with zipfile.ZipFile(output/"source-snapshot.zip","x",zipfile.ZIP_DEFLATED) as archive:
        for p in source_paths: archive.write(p,p.as_posix())
    manifest["source_snapshot_sha256"]=file_hash(output/"source-snapshot.zip")
    (output/"run-manifest.json").write_text(canonical_json(manifest)+"\n",encoding="utf-8")
    return summary


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--dataset-root",default="data/dataset")
    parser.add_argument("--inspect",action="store_true")
    parser.add_argument("--output",default="experiments/E003_domain_model_adequacy/results/E003-R001")
    parser.add_argument("--max-rows-per-file",type=int,default=2000)
    args=parser.parse_args()
    if args.inspect:
        target=Path("data/manifests/openrca.json")
        target.parent.mkdir(parents=True,exist_ok=True)
        with target.open("x",encoding="utf-8") as f:
            f.write(canonical_json(inspect_dataset(args.dataset_root))+"\n")
        print(target)
    else:
        run(args.dataset_root,args.output,args.max_rows_per_file)


if __name__=="__main__": main()
