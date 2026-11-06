"""Versioned structural priors. No labels, scenario, time, IO or ML in rank functions."""
from collections import Counter, defaultdict
import hashlib
import json

METHODS = ('symbolic_topology_v1', 'activity_reference_v1', 'graph_disabled_uniform_v1')


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                    ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def ranked(scores, rule, explanations=None, abstention=None):
    return {'rule_version':rule, 'abstention':abstention,
            'ranking':[] if abstention else [{'resource_id':n, 'score':scores[n],
                'supporting_callers':(explanations or {}).get(n, [])}
                for n in sorted(scores, key=lambda n:(-scores[n], n))],
            'epistemic_status':'STRUCTURAL_PRIOR_NOT_OBSERVED_FAULT'}


def topology_rank(nodes, edges):
    nodes = set(nodes)
    parents = {n:set() for n in nodes}
    for source, target in edges:
        if source not in nodes or target not in nodes:
            raise ValueError('unknown graph endpoint')
        if source != target:
            parents[target].add(source)
    if not any(parents.values()):
        return ranked({}, METHODS[0], abstention='NO_OBSERVED_INTER_COMPONENT_CALLS')
    callers = {}
    for node in sorted(nodes):
        visited = {node}
        pending = list(parents[node])
        while pending:
            caller = pending.pop()
            if caller not in visited:
                visited.add(caller)
                pending.extend(parents[caller]-visited)
        callers[node] = sorted(visited-{node})
    return ranked({n:len(callers[n]) for n in nodes}, METHODS[0], callers)


def activity_rank(counts):
    if not counts:
        return ranked({}, METHODS[1], abstention='NO_OBSERVED_RESOURCES')
    if any(not isinstance(v, int) or v <= 0 for v in counts.values()):
        raise ValueError('invalid observation count')
    return ranked(dict(counts), METHODS[1])


def uniform_rank(nodes):
    if not nodes:
        return ranked({}, METHODS[2], abstention='NO_OBSERVED_RESOURCES')
    return ranked(dict.fromkeys(nodes, 0), METHODS[2])


def infer(features, reverse=False):
    nodes = list(features['nodes'])
    edges = [(e['source'], e['target']) for e in features['edges']]
    counts = dict(features['observation_counts'])
    if reverse:
        nodes.reverse()
        edges.reverse()
        counts = dict(reversed(list(counts.items())))
    return {METHODS[0]:topology_rank(nodes, edges), METHODS[1]:activity_rank(counts),
            METHODS[2]:uniform_rank(nodes)}


def extract(payload):
    """Strict operational certificate extraction; no label/scenario parameter."""
    if set(payload) != {'observations','edges','trace_states','start_ns','cutoff_ns'}:
        raise ValueError('unexpected projection fields')
    common = {'object_id','event_ns','signal','resource_id'}
    extras = {'metric':{'metric_id','value','unit','temporality','kind'},
              'span':{'trace_id','span_id','parent_span_id','duration_raw','duration_unit'},
              'log':{'severity','message_available'}}
    by_id, spans, counts = {}, defaultdict(list), Counter()
    for o in payload['observations']:
        if o['signal'] not in extras or set(o) != common|extras[o['signal']]:
            raise ValueError('unexpected observation fields')
        if not payload['start_ns'] <= o['event_ns'] <= payload['cutoff_ns']:
            raise ValueError('future/out-of-window observation')
        if o['object_id'] in by_id:
            raise ValueError('duplicate observation')
        if not o['resource_id'].startswith('resource:') or len(o['resource_id']) != 73:
            raise ValueError('nonopaque resource')
        by_id[o['object_id']] = o
        counts[o['resource_id']] += 1
        if o['signal'] == 'span':
            spans[(o['trace_id'],o['span_id'])].append(o)
    expected, states = Counter(), Counter()
    for o in payload['observations']:
        if o['signal'] != 'span':
            continue
        p = o['parent_span_id']
        matches = spans.get((o['trace_id'],p), [])
        state = ('missing_parent_or_root_unknown' if not p else
                 'self_parent_convention_unknown' if p == o['span_id'] else
                 'unresolved_parent' if not matches else
                 'ambiguous_parent' if len(matches)>1 else 'resolved_parent')
        states[state] += 1
        if state == 'resolved_parent':
            expected[(matches[0]['object_id'],o['object_id'])] += 1
    collapsed, actual, edge_ids = {}, Counter(), set()
    for e in payload['edges']:
        if set(e) != {'id','source','target','relation','evidence','epistemic_status'}:
            raise ValueError('unexpected edge fields')
        if e['id'] in edge_ids or len(e['evidence']) != 2:
            raise ValueError('duplicate/unsupported edge')
        edge_ids.add(e['id'])
        support = [by_id.get(oid) for oid in e['evidence']]
        if any(o is None or o['signal'] != 'span' for o in support):
            raise ValueError('missing supporting spans')
        p, c = support
        if (p['resource_id'],c['resource_id']) != (e['source'],e['target']):
            raise ValueError('unsupported edge endpoints')
        if p['trace_id'] != c['trace_id'] or p['span_id'] != c['parent_span_id']:
            raise ValueError('unsupported trace parent')
        if e['relation'] != 'CALLS' or e['epistemic_status'] != 'OBSERVED':
            raise ValueError('unsupported relation')
        actual[tuple(e['evidence'])] += 1
        pair = e['source'],e['target']
        if pair not in collapsed:
            collapsed[pair] = {'source':pair[0], 'target':pair[1], 'multiplicity':0,
                              'representative_edge_id':e['id'], 'evidence':e['evidence']}
        collapsed[pair]['multiplicity'] += 1
    if expected != actual or dict(states) != payload['trace_states']:
        raise ValueError('trace/evidence conservation failure')
    return {'nodes':sorted(counts), 'observation_counts':dict(sorted(counts.items())),
            'edges':[collapsed[p] for p in sorted(collapsed)],
            'trace_states':dict(sorted(states.items()))}


def credits(result, root, k):
    rows = result['ranking']
    position = next((i for i,r in enumerate(rows) if r['resource_id']==root), None)
    if position is None:
        return {'tie_aware':0.0, 'deterministic':0}
    score = rows[position]['score']
    higher = sum(r['score']>score for r in rows)
    tied = sum(r['score']==score for r in rows)
    return {'tie_aware':max(0.0,min(1.0,(k-higher)/tied)),
            'deterministic':int(position<k)}
