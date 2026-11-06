"""Single, non-overwriting E004-R001 execution from accepted replay artifacts."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import statistics
import subprocess
import sys
import time
import traceback
import zipfile
from dce_foundation.symbolic_e004 import METHODS, credits, digest, extract, infer

ROOT = Path(__file__).resolve().parents[1]
EXPERIMENT = ROOT/'experiments/E004_symbolic_rca_baseline'


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def load(path):
    return json.loads(path.read_text(encoding='utf-8'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8', newline='\n') as stream:
        stream.write(value if isinstance(value,str) else json.dumps(value,indent=2,sort_keys=True,allow_nan=False))
        stream.write('\n')


def command(args):
    p=subprocess.run(args, cwd=ROOT, capture_output=True, text=True)
    return {'command':args,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}


def expected_parent_files(parent):
    manifest=load(parent/'artifact-manifest.json')
    files={parent/name:info for name,info in manifest['files'].items()}
    files[parent/'artifact-manifest.json']={'sha256':sha(parent/'artifact-manifest.json'),
                                         'bytes':(parent/'artifact-manifest.json').stat().st_size}
    integrity=load(parent/'parent-integrity.json')
    for run, entries in integrity['after'].items():
        for name, info in entries.items():
            files[parent.parent/run/name]=info
    return files


def verify_files(files):
    for path, info in files.items():
        if not path.is_file() or path.stat().st_size!=info['bytes'] or sha(path)!=info['sha256']:
            raise ValueError('preserved input artifact changed: '+str(path))


def evaluate(predictions, windows, labels):
    label_by_handle={}
    for label in labels:
        handle='context:'+digest([label['scenario'],label['fault_ns']-300*10**9,label['fault_ns']])
        if handle in label_by_handle:
            raise ValueError('duplicate evaluator window')
        label_by_handle[handle]=label
    if set(label_by_handle)!={w['window_identity'] for w in windows}:
        raise ValueError('label/window population mismatch')
    rows=[]
    for window, prediction in zip(windows,predictions,strict=True):
        label=label_by_handle[window['window_identity']]
        component=label['raw']['component']
        if not isinstance(component,str) or not component:
            raise ValueError('missing exact component label')
        root='resource:'+digest(['resource',[label['scenario'],component]])
        row={'handle':window['window_identity'],'scenario':label['scenario'],
             'incident_id':label['incident_id'],'root_resource':root,
             'root_present':root in prediction['candidate_nodes'],
             'candidate_count':len(prediction['candidate_nodes']),
             'has_calls':prediction['has_calls'],'methods':{}}
        for method,result in prediction['methods'].items():
            row['methods'][method]={'abstained':result['abstention'] is not None,
                                   'top1':credits(result,root,1),'top3':credits(result,root,3)}
        rows.append(row)
    return rows


def tables(rows):
    groups={'ALL':rows}
    for scenario in sorted({r['scenario'] for r in rows}):
        groups[scenario]=[r for r in rows if r['scenario']==scenario]
    result={}
    for scenario,cases in groups.items():
        n=len(cases)
        methods={}
        for method in METHODS:
            methods[method]={'abstentions':sum(r['methods'][method]['abstained'] for r in cases)}
            for k in ('top1','top3'):
                for policy in ('tie_aware','deterministic'):
                    methods[method][k+'_'+policy]=statistics.mean(r['methods'][method][k][policy] for r in cases)
        deltas={}
        for reference in METHODS[1:]:
            for k in ('top1','top3'):
                values=[r['methods'][METHODS[0]][k]['tie_aware']-r['methods'][reference][k]['tie_aware'] for r in cases]
                mean=statistics.mean(values)
                half=1.96*statistics.stdev(values)/math.sqrt(n) if n>1 else 0
                deltas[reference+'_'+k]={'paired_mean':mean,'descriptive_95_interval':[mean-half,mean+half],
                                        'not_valid_significance_under_dependent_windows':True}
        result[scenario]={'cases':n,'root_present':sum(r['root_present'] for r in cases),
            'root_absent':sum(not r['root_present'] for r in cases),
            'cases_with_inter_component_calls':sum(r['has_calls'] for r in cases),
            'methods':methods,'paired_deltas':deltas}
    return result


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output', default=str(EXPERIMENT/'results/E004-R001'))
    output=Path(parser.parse_args().output).resolve()
    if output.exists():
        raise FileExistsError('run already exists; no overwrite: '+str(output))
    if output != (EXPERIMENT/'results/E004-R001').resolve():
        raise ValueError('only registered E004-R001 output is authorized')
    output.mkdir(parents=True)
    for folder in ('logs','certificates'):
        (output/folder).mkdir()
    config=load(EXPERIMENT/'configuration.yaml')
    parent=ROOT/config['input_root']
    started=time.perf_counter()
    completed=0
    phase='preflight'
    log=(output/'logs/execution.jsonl').open('x',encoding='utf-8')

    def emit(**info):
        line=json.dumps({'time_utc':datetime.now(timezone.utc).isoformat(),'phase':phase,**info})
        log.write(line+'\n'); log.flush()
        print(line,flush=True)

    def guard():
        free=shutil.disk_usage(ROOT).free
        if free<config['minimum_free_disk_bytes']:
            raise RuntimeError('disk safety floor reached')
        return free

    try:
        if not sys.flags.no_user_site:
            raise RuntimeError('invoke Python with -s to disable user site')
        if config['expected_windows']!=335 or config['repetitions']!=2 or tuple(config['methods'])!=METHODS:
            raise ValueError('unregistered configuration')
        guard()
        qualification=command([sys.executable,'-s','scripts/check_e004_governance.py'])
        tests=command([sys.executable,'-s','-m','unittest','discover','-s','tests','-p','test_e004*.py','-v'])
        write(output/'logs/qualification.json',qualification)
        write(output/'logs/tests.json',tests)
        if qualification['exit_code'] or tests['exit_code']:
            raise RuntimeError('qualification or fixture tests failed')
        inventory=load(parent/'replay1-inventory.json')
        windows=inventory['windows']
        if len(windows)!=335 or len({w['window_identity'] for w in windows})!=335:
            raise ValueError('invalid fixed population')
        preserved=expected_parent_files(parent)
        emit(message='verifying inherited evidence before execution',files=len(preserved))
        verify_files(preserved)
        source_paths=sorted(list(EXPERIMENT.glob('*.md'))+[EXPERIMENT/'configuration.yaml',
            ROOT/'src/dce_foundation/symbolic_e004.py',ROOT/'scripts/run_e004.py',ROOT/'scripts/audit_e004.py',
            ROOT/'scripts/check_e004_governance.py',ROOT/'tests/test_e004_symbolic.py',ROOT/'tests/test_e004_independent.py',
            ROOT/'EXPERIMENT_INDEX_AMENDMENT_2026-10-06_E004.md',ROOT/'docs/governance/registrations/E004.json',
            ROOT/'docs/governance/amendments/2026-10-06-E003-V006-acceptance-and-E004-scope.md',
            ROOT/'src/dce_foundation/qualification/projection.py',ROOT/'src/dce_foundation/domain.py'])
        sources={str(p.relative_to(ROOT).as_posix()):sha(p) for p in source_paths}
        with zipfile.ZipFile(output/'source-snapshot.zip','x',compression=zipfile.ZIP_DEFLATED) as archive:
            for p in source_paths:
                archive.write(p,str(p.relative_to(ROOT).as_posix()))
        label_path=parent/'evaluation-labels.json'
        preflight={'run_id':'E004-R001','configuration':config,'sources':sources,
            'source_snapshot_sha256':sha(output/'source-snapshot.zip'),
            'git_head':command(['git','rev-parse','HEAD']), 'git_status':command(['git','status','--porcelain']),
            'input_inventory_sha256':sha(parent/'replay1-inventory.json'),
            'label_sha256_before':sha(label_path),'label_content_parsed_before_predictions':False,
            'frozen_at_utc':datetime.now(timezone.utc).isoformat(),
            'environment':{'python':sys.version,'executable':sys.executable,'platform':platform.platform(),
                'processor':os.environ.get('PROCESSOR_IDENTIFIER',platform.processor()),'logical_cpus':os.cpu_count(),
                'no_user_site':bool(sys.flags.no_user_site),'sys_path':sys.path,
                'dependencies':'standard library only; virtualenv has system site enabled; no claim of complete isolation',
                'peak_memory':'NOT MEASURED'},
            'random_seed':None,'randomness':'none; deterministic order reversal for repeat',
            'dataset_rescanned':False,'disk_free_bytes':guard(),
            'preserved_files':{str(p.relative_to(ROOT).as_posix()):v for p,v in preserved.items()}}
        write(output/'preflight.json',preflight)
        write(output/'input-manifest.json',{'inventory_sha256':preflight['input_inventory_sha256'],
            'windows':[{k:w[k] for k in ('window_identity','scenario','start_ns','fault_ns','artifact_path','artifact_sha256','canonical_sha256')} for w in windows]})
        phase='inference'
        predictions=[]
        repeat_hashes=[]
        with (output/'predictions.jsonl').open('x',encoding='utf-8') as stream:
            for window in windows:
                guard()
                path=Path(window['artifact_path'])
                if sha(path)!=window['artifact_sha256']:
                    raise ValueError('input byte hash mismatch')
                with gzip.open(path,'rb') as gz:
                    payload=json.loads(gz.read())
                if digest(payload)!=window['canonical_sha256'] or (payload['start_ns'],payload['cutoff_ns'])!=(window['start_ns'],window['fault_ns']):
                    raise ValueError('canonical input or window mismatch')
                features=extract(payload)
                first=infer(features)
                second=infer(features,reverse=True)
                if first!=second:
                    raise ValueError('repeatability failed')
                certificate=window['window_identity'].replace(':','-')+'.json'
                write(output/'certificates'/certificate,features)
                record={'handle':window['window_identity'],'candidate_nodes':features['nodes'],
                        'has_calls':any(e['source']!=e['target'] for e in features['edges']),
                        'certificate':certificate,'certificate_sha256':sha(output/'certificates'/certificate),
                        'methods':first,'repeat1_sha256':digest(first),'repeat2_sha256':digest(second)}
                stream.write(json.dumps(record,sort_keys=True)+'\n'); stream.flush()
                predictions.append(record)
                repeat_hashes.append({'handle':record['handle'],'first':digest(first),'second':digest(second)})
                completed+=1
                emit(completed=completed,total=335)
                del payload,features,first,second
        prediction_sha=sha(output/'predictions.jsonl')
        write(output/'prediction-seal.json',{'prediction_sha256':prediction_sha,'count':completed,
            'sealed_at_utc':datetime.now(timezone.utc).isoformat(),'evaluator_labels_opened':False})
        write(output/'repeatability.json',{'repetitions':2,'equal':True,'cases':repeat_hashes})
        phase='evaluation'
        emit(message='335 predictions sealed; evaluator may now open labels')
        labels=load(label_path)
        rows=evaluate(predictions,windows,labels)
        metrics=tables(rows)
        write(output/'case-results.json',rows)
        write(output/'metrics.json',metrics)
        phase='independent_audit'
        audit=command([sys.executable,'-s','scripts/audit_e004.py','--run',str(output)])
        write(output/'logs/audit-process.json',audit)
        if audit['exit_code'] or not load(output/'independent-audit.json')['passed']:
            raise RuntimeError('independent audit failed')
        phase='finalization'
        emit(message='independent audit passed; verifying preserved evidence')
        verify_files(preserved)
        for name,h in sources.items():
            if sha(ROOT/name)!=h:
                raise ValueError('executed source changed after freeze: '+name)
        if sha(label_path)!=preflight['label_sha256_before'] or sha(output/'predictions.jsonl')!=prediction_sha:
            raise ValueError('label or sealed predictions modified')
        write(output/'preservation.json',{'passed':True,'files_verified':len(preserved),
            'V002_V004_V005_V006_unchanged':True,'raw_dataset_rescanned':False})
        summary={'run_id':'E004-R001','status':'Completed','technical_gate':'PASS',
            'cases':335,'repeatability_cases':335,'repetitions':2,'independent_audit_passed':True,
            'methods':list(METHODS),'overall':metrics['ALL'],
            'elapsed_seconds':time.perf_counter()-started,'disk_free_bytes':guard(),
            'scientific_decision_proposal':'REVISE / structural prior only; human review pending',
            'superiority_established':False,'symptom_detector':'NONE','online_detection_tested':False,
            'official_openrca_score':False,'dataset_rescanned':False,'successor_started':False}
        write(output/'summary.json',summary)
        table=['| Method | Top-1 (tie-aware) | Top-3 (tie-aware) | Abstentions |','|---|---:|---:|---:|']
        for name,m in metrics['ALL']['methods'].items():
            table.append(f"| {name} | {100*m['top1_tie_aware']:.2f}% | {100*m['top3_tie_aware']:.2f}% | {m['abstentions']} |")
        decision='# E004-R001: what we learned\n\nAll 335 cases were processed twice. The technical repeatability and independent-audit gate passed.\n\n'+ '\n'.join(table)
        decision+=f"\n\nThe labelled component appears among observed candidates in {metrics['ALL']['root_present']}/335 cases. Cases without it remain in the denominator.\n\n"
        decision+='This ranks structural candidates, not measured faulty symptoms. A heavily shared dependency is not necessarily broken. Missing traces do not prove no dependency. UNKNOWN metric semantics remain unresolved. Supplied fault times define retrospective windows: this is not online detection, official query scoring, causal inference or evidence of hybrid superiority. The descriptive paired intervals do not establish significance under overlapping windows.\n\nDecision proposal: REVISE / restricted diagnostic readiness. Review the results before authorizing symptom qualification or another experiment. No successor has started.\n'
        write(output/'decision.md',decision)
        write(output/'results.json',{'summary':summary,'per_system':metrics,'case_results_file':'case-results.json',
            'predictions_file':'predictions.jsonl','repeatability_file':'repeatability.json'})
        write(output/'run.md',f'# E004-R001 execution\n\nStarted with frozen v1 protocol; completed {datetime.now(timezone.utc).isoformat()} UTC.\n\nInvocation: python -s scripts/run_e004.py (PYTHONPATH=src, PYTHONDONTWRITEBYTECODE=1). Preflight records exact interpreter, code/configuration hashes, source snapshot, Git dirty state, hardware, parent files and input inventory. Fixtures and subprocess stdout/stderr are in logs/. Predictions were sealed before evaluator label parsing. Independent audit and predecessor preservation passed. No raw data read, old record edited, commit or push. Human review pending.\n')
        emit(message='completed',technical_gate='PASS',cases=335)
        log.close()
        manifest={str(p.relative_to(output).as_posix()):{'sha256':sha(p),'bytes':p.stat().st_size}
                  for p in sorted(output.rglob('*')) if p.is_file()}
        write(output/'artifact-manifest.json',{'run_id':'E004-R001','files':manifest,
            'external_inputs':'input-manifest.json','status':'Completed'})
    except Exception as exc:
        traceback.print_exc()
        emit(error=str(exc),completed=completed)
        log.close()
        write(output/'failure.json',{'run_id':'E004-R001','phase':phase,'error':str(exc),
            'completed_cases':completed,'no_successor_started':True,'scientific_results_not_fabricated':True})
        raise


if __name__=='__main__':
    main()
