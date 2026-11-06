"""Inference input builder has no label/query parameter or evaluator database access."""
from collections import defaultdict,Counter
from decimal import Decimal,InvalidOperation
from ..domain import digest


def token(kind,value):
    return kind+':'+digest([kind,value])


def projected_row(oid,ns,signal,environment,raw):
    """Names/paths/free text are audit-only; values remain exact source strings."""
    identity = raw.get('cmdb_id') or raw.get('service') or raw.get('tc') or raw.get('serviceName')
    if not identity:
        raise ValueError('missing source identity')
    oid=token('observation',oid)
    common = {'object_id':oid,'event_ns':ns,'signal':signal,
              'resource_id':token('resource',[environment,identity])}
    if signal=='log':
        return [{**common,'severity':'UNKNOWN','message_available':bool(raw.get('value'))}]
    if signal=='span':
        trace = raw.get('trace_id',raw.get('traceId'))
        span = raw.get('span_id',raw.get('id'))
        parent = raw.get('parent_id',raw.get('parent_span',raw.get('pid'))) or None
        if not trace or not span:
            raise ValueError('missing trace/span identifier')
        return [{**common,'trace_id':token('trace',[environment,trace]),'span_id':token('span',[environment,trace,span]),
                 'parent_span_id':token('span',[environment,trace,parent]) if parent else None,
                 'duration_raw':raw.get('duration',raw.get('elapsedTime')) or None,'duration_unit':'UNKNOWN'}]
    allowed_wide={'rr','sr','cnt','mrt','count','avg_time','num','succee_num','succee_rate'}
    values = [(raw.get('kpi_name',raw.get('name')),raw['value'])] if 'value' in raw else [
        (k,v) for k,v in raw.items() if k in allowed_wide]
    for name,value in values:
        try:
            if not name or (value and not Decimal(value).is_finite()):
                raise ValueError('invalid metric')
        except InvalidOperation as exc:
            raise ValueError('nonnumeric metric') from exc
    return [{**common,'object_id':oid+':'+token('metric',name),'metric_id':token('metric',[environment,name]),
             'value':value or None,'unit':'UNKNOWN','temporality':'UNKNOWN','kind':'UNKNOWN'} for name,value in values]


def query_projection(rows,start,cutoff):
    observations = []
    for oid,ns,signal,environment,raw in rows:
        if start <= ns <= cutoff:
            observations.extend(projected_row(oid,ns,signal,environment,raw))
    observations.sort(key=lambda o:(o['event_ns'],o['object_id']))
    spans=defaultdict(list)
    for o in observations:
        if o['signal']=='span':
            spans[(o['trace_id'],o['span_id'])].append(o)
    edges=[]
    states=Counter()
    for o in observations:
        if o['signal']!='span':
            continue
        parent=o['parent_span_id']
        if not parent:
            state='missing_parent_or_root_unknown'
        elif parent==o['span_id']:
            state='self_parent_convention_unknown'
        else:
            matches=spans.get((o['trace_id'],parent),[])
            state='unresolved_parent' if not matches else ('ambiguous_parent' if len(matches)>1 else 'resolved_parent')
            if state=='resolved_parent':
                p=matches[0]
                edges.append({'id':token('edge',[p['object_id'],o['object_id']]),'source':p['resource_id'],
                              'target':o['resource_id'],'relation':'CALLS','evidence':[p['object_id'],o['object_id']],
                              'epistemic_status':'OBSERVED'})
        states[state]+=1
    edges.sort(key=lambda e:e['id'])
    return {'observations':observations,'edges':edges,'trace_states':dict(sorted(states.items())),
            'start_ns':start,'cutoff_ns':cutoff}


def projection_violations(projected):
    errors=[]
    a,b=projected['start_ns'],projected['cutoff_ns']
    ids={o['object_id']:o for o in projected['observations']}
    forbidden={'root_entity','fault_type','reason','ground_truth','scoring_points','instruction','source_path','source_row','message','status_raw'}
    for o in projected['observations']:
        if not a<=o['event_ns']<=b:
            errors.append('future/out-of-window observation')
        if forbidden.intersection(o):
            errors.append('forbidden projected field')
    for e in projected['edges']:
        if e['relation']!='CALLS' or len(e['evidence'])!=2 or any(x not in ids or ids[x]['signal']!='span' for x in e['evidence']):
            errors.append('unsupported or temporally unavailable edge evidence')
    return errors
