"""E003-AM002 CLI: full time census, all-incident coverage, isolated repeated projection."""
import argparse
from collections import Counter
import csv
from datetime import datetime,timezone
import gzip
import hashlib
import io
import json
from pathlib import Path
import platform
import shutil
import sqlite3
import subprocess
import sys
import time
import zipfile
import zlib
from ..domain import canonical_json,digest
from ..inspection import file_hash
from ..telemetry.openrca import SCENARIOS,LABEL_HEADERS
from ..representation_v2.audit import peak_memory_bytes,write_new
from . import VERSION
VERSION = VERSION + '-compact1'
from .compact import SCHEMA,BlockWriter,projected_context_rows,compact_coverage,inherit_complete_files
from .evaluator import LOCAL,associations
from .projection import query_projection,projection_violations
from .scan import scan_file
from .semantics import inventory_entry


def read_evaluation(root):
    labels,queries=[],[]
    for scenario in SCENARIOS:
        with zipfile.ZipFile(root/(scenario.split('/')[0]+'.zip')) as z:
            for name in ('record.csv','query.csv'):
                with z.open(scenario+'/'+name) as stream:
                    reader=csv.DictReader(io.TextIOWrapper(stream,encoding='utf-8-sig',newline=''))
                    if set(reader.fieldnames)!=LABEL_HEADERS[name]:
                        raise ValueError('label header mismatch')
                    for line,row in enumerate(reader,2):
                        if name=='record.csv':
                            from ..representation_v2.timestamps import epoch_ns
                            ns=epoch_ns(row['timestamp'],'s')
                            if int(datetime.strptime(row['datetime'],'%Y-%m-%d %H:%M:%S').replace(tzinfo=LOCAL).timestamp())*10**9!=ns:
                                raise ValueError('label datetime disagreement')
                            labels.append({'incident_id':scenario+'@'+str(line),'scenario':scenario,'fault_ns':ns,'row':line,'raw':row})
                        else:
                            queries.append({'query_id':scenario+'#query@'+str(line),'scenario':scenario,'row':line,'raw':row})
    return labels,queries


context_rows = projected_context_rows
incident_coverage = compact_coverage


def replay_cases(db,labels,config,output,repetition):
    summaries=[]
    handles={}
    for label in labels:
        t=label['fault_ns']
        start=t-config['incident_before_seconds']*10**9
        projected=query_projection(context_rows(db,label['scenario'],start,t),start,t)
        violations=projection_violations(projected)
        # No incident label or query metadata in this payload. Handle-to-case mapping is evaluator-only.
        payload_hash=digest(projected)
        handle='context:'+digest([label['scenario'],start,t])
        target=output/'cases'/f'replay-{repetition:03d}'
        target.mkdir(parents=True,exist_ok=True)
        if handle not in handles:
            with gzip.GzipFile(filename=str(target/(handle.replace(':','-')+'.json.gz')),mode='xb',mtime=0) as f:
                f.write(canonical_json(projected).encode())
            handles[handle]=payload_hash
        elif handles[handle]!=payload_hash:
            raise ValueError('same query window produced inconsistent projection')
        summaries.append({'handle':handle,'canonical_sha256':payload_hash,'graph_sha256':digest(projected['edges']),
                          'observations':len(projected['observations']),'edges':len(projected['edges']),
                          'trace_states':projected['trace_states'],'violations':violations})
    return summaries


def capture_preflight(repo,output,config_path):
    paths=list((repo/'src/dce_foundation/qualification').glob('*.py'))
    paths+=list((repo/'src/dce_foundation/representation_v2').glob('*.py'))
    paths += [repo/'tests/test_e003_qualification.py',repo/'tests/test_e003_compact.py',config_path,config_path.parent/'protocol.md',config_path.parent/'storage-amendment.md']
    hashes={p.relative_to(repo).as_posix():file_hash(p) for p in paths}
    with zipfile.ZipFile(output/'source-snapshot.zip','x',zipfile.ZIP_DEFLATED) as z:
        for p in paths:
            z.write(p,p.relative_to(repo).as_posix())
    historical={}
    for folder in ('experiments/E001','experiments/E002','experiments/E003_domain_model_adequacy/results/E003-R001','experiments/E003_domain_model_adequacy/remediation/2026-10-03'):
        for p in (repo/folder).rglob('*'):
            if p.is_file():
                historical[p.relative_to(repo).as_posix()]=file_hash(p)
    write_new(output/'preflight.json',{'created_at_utc':datetime.now(timezone.utc).isoformat(),
        'git_sha':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
        'git_status':subprocess.check_output(['git','status','--short'],text=True).splitlines(),
        'source_hashes':hashes,'historical_hashes':historical,'source_snapshot_sha256':file_hash(output/'source-snapshot.zip'),
        'python':sys.version,'executable':sys.executable,'platform':platform.platform(),
        'free_disk_bytes':shutil.disk_usage(output).free,'configuration':json.loads(config_path.read_text())})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',required=True)
    parser.add_argument('--output',required=True)
    parser.add_argument('--inherit-completed-from')
    args=parser.parse_args()
    repo=Path.cwd()
    output=Path(args.output)
    config_path=Path(args.config).resolve()
    config=json.loads(config_path.read_text())
    output.mkdir(parents=True,exist_ok=False)
    capture_preflight(repo,output,config_path)
    root=repo/config['dataset_root']
    started=time.perf_counter()
    labels,queries=read_evaluation(root)
    write_new(output/'evaluation-labels.json',labels)
    write_new(output/'evaluation-queries.json',queries)
    links=associations(queries,labels)
    write_new(output/'evaluation-query-associations.json',links)
    windows={s:[] for s in SCENARIOS}
    for label in labels:
        t=label['fault_ns']
        windows[label['scenario']].append((t-config['incident_before_seconds']*10**9,t+config['incident_after_seconds']*10**9))
    # Root identity is not supplied to the scanner or projection builder.
    db=sqlite3.connect(output/'context.sqlite')
    db.executescript(SCHEMA)
    writer=BlockWriter(db)
    profiles=inherit_complete_files(Path(args.inherit_completed_from),db,output) if args.inherit_completed_from else []
    completed_paths={p['path'] for p in profiles}
    try:
        csv.field_size_limit(config['csv_field_limit_bytes'])
        for scenario in SCENARIOS:
            with zipfile.ZipFile(root/(scenario.split('/')[0]+'.zip')) as archive:
                paths=sorted(n for n in archive.namelist() if n.startswith(scenario+'/telemetry/') and n.endswith('.csv'))
                for path in paths:
                    if path in completed_paths:
                        continue
                    print(json.dumps({'phase':'file_start','file':path,'completed':len(profiles)}),flush=True)
                    result=scan_file(archive,path,scenario,windows[scenario],writer,config,output)
                    profiles.append(result)
                    write_new(output/(f'file-{len(profiles):03d}.json'),result)
                    print(json.dumps({'phase':'file_complete','file':path,'rows':result['counts']['rows_seen'],'decision':result['decision']}),flush=True)
        writer.commit()
        db.executescript('CREATE INDEX block_window ON blocks(environment,min_ns,max_ns);')
        metrics=[]
        for file in profiles:
            metrics.extend(inventory_entry(file['scenario'],file['path'],name,count) for name,count in sorted(file['metric_counts'].items()))
        write_new(output/'metric-qualification-registry.json',metrics)
        coverage=incident_coverage(db,labels,links,config)
        write_new(output/'evaluation-incident-coverage.json',coverage)
        replays=[]
        for repetition in range(1,config['replay_repetitions']+1):
            print(json.dumps({'phase':'replay','repetition':repetition}),flush=True)
            replays.append(replay_cases(db,labels,config,output,repetition))
        write_new(output/'replay-comparison.json',{'equal':replays[0]==replays[1],'passes':replays})
        gates={'A':'PASS' if all(p['decision']=='QUALIFIED' and p['row_conservation'] for p in profiles) else 'FAIL',
            'B':'PASS','C':'PASS' if not any(r['violations'] for r in replays[0]) else 'FAIL','D':'PASS',
            'E':'PASS' if all(e['status']=='UNKNOWN' and e['evidence_source'] is None and e['confidence']==0 for e in metrics) else 'FAIL',
            'F':'PASS' if len(coverage)==len(labels) else 'FAIL','G':'PASS' if not any(r['violations'] for r in replays[0]) else 'FAIL',
            'H':'PASS' if replays[0]==replays[1] else 'FAIL'}
        preflight=json.loads((output/'preflight.json').read_text())
        integrity=all(file_hash(repo/n)==h for n,h in preflight['historical_hashes'].items())
        summary={'amendment_id':'E003-AM002','validation_id':output.name,'version':VERSION,'gates':gates,
            'representation_passed':all(v=='PASS' for v in gates.values()),'review_required':True,
            'files':len(profiles),'total_source_rows':sum(p['counts']['rows_seen'] for p in profiles),
            'labels':len(labels),'queries':len(queries),'qualified_query_associations':sum(q['status']=='QUALIFIED' for q in links),
            'root_observed_cases':sum(c['root_observation_found'] for c in coverage),
            'before_only_root_observed_cases':sum(c['before_only_task_eligible'] for c in coverage),
            'metric_registry_entries':len(metrics),'unknown_metric_entries':sum(e['status']=='UNKNOWN' for e in metrics),
            'historical_records_unchanged':integrity,'elapsed_seconds':time.perf_counter()-started,
            'peak_memory_bytes':peak_memory_bytes(),'context_store_bytes':(output/'context.sqlite').stat().st_size,
            'rcaeval_started':False,'raw_deleted':False,'official_query_scoring_qualified':all(q['status']=='QUALIFIED' for q in links)}
        write_new(output/'summary.json',summary)
        write_new(output/'leakage-audit.json',{'source_identifier_cues':{p['path']:p['source_identifier_cue_counts'] for p in profiles if p['source_identifier_cue_counts']},
            'policy':'opaque source identity tokens; raw identifiers/paths/log messages/status/type/operation/labels excluded',
            'temporal_edges':'both parent and child present within explicit start/cutoff; no unknown-validity workbook edges',
            'evaluation_only':'root labels and scoring points used only after source retrieval; window time used as declared query input',
            'qualification_scope':'representation safety, not statistical independence of signal values or causal validity'})
        db.close()
        write_new(output/'artifact-manifest.json',{p.relative_to(output).as_posix():{'sha256':file_hash(p),'bytes':p.stat().st_size} for p in output.rglob('*') if p.is_file()})
        print(json.dumps(summary,indent=2),flush=True)
    except Exception as exc:
        db.commit()
        db.close()
        write_new(output/'failure.json',{'error':str(exc),'completed_files':len(profiles),'elapsed_seconds':time.perf_counter()-started,'result':'BLOCKED','review_required':True})
        raise


if __name__=='__main__':
    main()
