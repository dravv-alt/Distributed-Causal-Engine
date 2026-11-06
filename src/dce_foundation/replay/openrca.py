import argparse
import json
from pathlib import Path
from ..domain import canonical_json
from ..graph import build_graph, build_evaluation_graph, graph_dict
from ..telemetry.openrca import OpenRCAAdapter
from ..validation import validate


def replay(root, incident_id, max_rows_per_file=None):
    incident=OpenRCAAdapter(root).load(incident_id,max_rows_per_file)
    graph=build_graph(incident)
    return incident,graph,validate(incident,graph)


def main():
    parser=argparse.ArgumentParser(description="OpenRCA representation replay; not RCA reasoning")
    parser.add_argument("--dataset-root",default="data/dataset")
    parser.add_argument("--incident",required=True,help="Bank@2, Market/cloudbed-1@2, etc.; source record line")
    parser.add_argument("--max-rows-per-file",type=int,default=None)
    parser.add_argument("--output",type=Path,help="new output directory; never overwrites existing results")
    args=parser.parse_args()
    incident,graph,report=replay(args.dataset_root,args.incident,args.max_rows_per_file)
    if args.output:
        args.output.mkdir(parents=True,exist_ok=False)
        for name,value in (("operational.json",incident.operational_dict()),("ground-truth.json",incident.to_dict()["ground_truth"]),
                           ("graph.json",graph_dict(graph)),("evaluation-graph.json",graph_dict(build_evaluation_graph(incident))),
                           ("validation.json",report)):
            (args.output/name).write_text(canonical_json(value)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2,ensure_ascii=False,allow_nan=False))
    if report["violations"] or report["source_rows_rejected"]:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
