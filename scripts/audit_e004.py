"""Independent compact-certificate and evaluator audit; does not import rank code."""
import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import statistics

ROOT=Path(__file__).resolve().parents[1]
METHODS=('symbolic_topology_v1','activity_reference_v1','graph_disabled_uniform_v1')


def load(p):
    return json.loads(p.read_text(encoding='utf-8'))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def canonical(v):
    return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(',', ':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()


def reference(features):
    nodes=features['nodes']
    reach={n:set() for n in nodes}
    valid=False
    for edge in features['edges']:
        a,b=edge['source'],edge['target']
        if a not in reach or b not in reach or len(edge['evidence'])!=2 or edge['multiplicity']<=0:
            raise ValueError('invalid certificate edge')
        if a!=b:
            reach[a].add(b); valid=True
    # Forward transitive closure: intentionally distinct from production reverse BFS.
    for pivot in nodes:
        for source in nodes:
            if pivot in reach[source]:
                reach[source].update(reach[pivot])
    callers={target:sorted(source for source in nodes if source!=target and target in reach[source]) for target in nodes}
    scores=({n:len(callers[n]) for n in nodes},features['observation_counts'],dict.fromkeys(nodes,0))
    result={}
    for i,method in enumerate(METHODS):
        reason='NO_OBSERVED_INTER_COMPONENT_CALLS' if i==0 and not valid else ('NO_OBSERVED_RESOURCES' if not nodes else None)
        rows=[] if reason else [{'resource_id':n,'score':scores[i][n],
            'supporting_callers':callers[n] if i==0 else []} for n in sorted(nodes,key=lambda n:(-scores[i][n],n))]
        result[method]={'rule_version':method,'abstention':reason,'ranking':rows,
                        'epistemic_status':'STRUCTURAL_PRIOR_NOT_OBSERVED_FAULT'}
    return result


def credit(rows,root,k):
    matches=[r for r in rows if r['resource_id']==root]
    if not matches:
        return {'tie_aware':0.0,'deterministic':0}
    score=matches[0]['score']
    group=[r for r in rows if r['score']==score]
    available=k-len([r for r in rows if r['score']>score])
    return {'tie_aware':min(len(group),max(0,available))/len(group),
            'deterministic':int(root in [r['resource_id'] for r in rows[:k]])}


def main():
    parser=argparse.ArgumentParser(); parser.add_argument('--run',required=True)
    run=Path(parser.parse_args().run)
    preflight=load(run/'preflight.json')
    parent=ROOT/preflight['configuration']['input_root']
    predictions=[json.loads(line) for line in (run/'predictions.jsonl').read_text().splitlines()]
    cases=load(run/'case-results.json'); windows=load(run/'input-manifest.json')['windows']
    seal=load(run/'prediction-seal.json')
    expected=load(parent/'replay-comparison.json')['passes'][0]
    expected_by_handle={r['handle']:r for r in expected}
    labels=load(parent/'evaluation-labels.json')
    label_map={'context:'+canonical([l['scenario'],l['fault_ns']-300*10**9,l['fault_ns']]):l for l in labels}
    errors=[]
    if len(predictions)!=335 or len(cases)!=335 or len({p['handle'] for p in predictions})!=335:
        errors.append('wrong population')
    if sha(run/'predictions.jsonl')!=seal['prediction_sha256']:
        errors.append('prediction seal hash mismatch')
    independently_scored=[]
    for p,c,w in zip(predictions,cases,windows,strict=True):
        try:
            if p['handle']!=c['handle'] or p['handle']!=w['window_identity']:
                raise ValueError('case join mismatch')
            f=load(run/'certificates'/p['certificate'])
            if sha(run/'certificates'/p['certificate'])!=p['certificate_sha256']:
                raise ValueError('certificate hash mismatch')
            if set(f)!= {'nodes','observation_counts','edges','trace_states'}:
                raise ValueError('unexpected operational certificate fields')
            if f['nodes']!=sorted(f['observation_counts']) or len(set(f['nodes']))!=len(f['nodes']):
                raise ValueError('candidate universe mismatch')
            oracle=expected_by_handle[p['handle']]
            if sum(f['observation_counts'].values())!=oracle['observations'] or sum(e['multiplicity'] for e in f['edges'])!=oracle['edges'] or f['trace_states']!=oracle['trace_states']:
                raise ValueError('inherited observation/edge/state totals disagree')
            ref=reference(f)
            if ref!=p['methods'] or canonical(ref)!=p['repeat1_sha256'] or p['repeat1_sha256']!=p['repeat2_sha256']:
                raise ValueError('independent rank or repeat mismatch')
            label=label_map[p['handle']]
            root='resource:'+canonical(['resource',[label['scenario'],label['raw']['component']]])
            if c['root_resource']!=root or c['root_present']!=(root in f['nodes']) or c['scenario']!=label['scenario']:
                raise ValueError('independent label join mismatch')
            expected_methods={m:{'abstained':ref[m]['abstention'] is not None,
                'top1':credit(ref[m]['ranking'],root,1),'top3':credit(ref[m]['ranking'],root,3)} for m in METHODS}
            if c['methods']!=expected_methods or p['candidate_nodes']!=f['nodes']:
                raise ValueError('independent score mismatch')
            independently_scored.append(c)
        except Exception as exc:
            errors.append({'handle':p['handle'],'error':str(exc)})
    metrics=load(run/'metrics.json')
    groups={'ALL':independently_scored}
    groups.update({s:[r for r in independently_scored if r['scenario']==s] for s in sorted({r['scenario'] for r in independently_scored})})
    for scenario,rows in groups.items():
        actual=metrics[scenario]
        if actual['cases']!=len(rows) or actual['root_present']!=sum(r['root_present'] for r in rows):
            errors.append('aggregate denominator/coverage mismatch')
        for m in METHODS:
            for k in ('top1','top3'):
                for policy in ('tie_aware','deterministic'):
                    value=sum(r['methods'][m][k][policy] for r in rows)/len(rows)
                    if not math.isclose(value,actual['methods'][m][k+'_'+policy],abs_tol=1e-12):
                        errors.append('aggregate scoring mismatch')
            if actual['methods'][m]['abstentions']!=sum(r['methods'][m]['abstained'] for r in rows):
                errors.append('abstention count mismatch')
        if actual['root_absent']!=sum(not r['root_present'] for r in rows) or actual['cases_with_inter_component_calls']!=sum(r['has_calls'] for r in rows):
            errors.append('coverage reporting mismatch')
        for baseline in METHODS[1:]:
            for k in ('top1','top3'):
                diffs=[r['methods'][METHODS[0]][k]['tie_aware']-r['methods'][baseline][k]['tie_aware'] for r in rows]
                avg=sum(diffs)/len(diffs)
                variance=sum((d-avg)**2 for d in diffs)/(len(diffs)-1) if len(diffs)>1 else 0
                margin=1.96*math.sqrt(variance/len(diffs))
                reported=actual['paired_deltas'][baseline+'_'+k]
                if not math.isclose(avg,reported['paired_mean'],abs_tol=1e-12) or any(not math.isclose(x,y,abs_tol=1e-12) for x,y in zip([avg-margin,avg+margin],reported['descriptive_95_interval'])):
                    errors.append('paired summary mismatch')
    if set(groups)!=set(metrics):
        errors.append('system reporting mismatch')
    if sha(parent/'evaluation-labels.json')!=preflight['label_sha256_before']:
        errors.append('evaluator labels changed')
    report={'run_id':'E004-R001','passed':not errors,'cases_checked':len(independently_scored),
        'errors':errors,'independent_algorithm':'forward transitive closure versus reverse BFS',
        'evaluator_recomputed':True,'production_rank_module_imported':False,
        'raw_projection_extraction_totals_checked_against_E003':True,
        'limitation':'Certificate audit is not a second raw-source scan; E003 canonical hashes underpin input identity.'}
    with (run/'independent-audit.json').open('x',encoding='utf-8') as stream:
        json.dump(report,stream,indent=2,sort_keys=True)
    print(json.dumps(report))
    if errors:
        raise SystemExit(1)


if __name__=='__main__':
    main()
