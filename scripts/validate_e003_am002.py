"""Read-only independent replay verification; writes only a new audit artifact.

Does not import the production projection builder or reinterpret source timestamps.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path

import networkx as nx


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()


def digest(value):
    encoded = json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(encoded.encode()).hexdigest()


def verify_projection(data):
    errors = []
    graph = nx.MultiDiGraph()
    by_id = {}
    trace_states = Counter()
    spans = {}
    common = {'object_id', 'event_ns', 'signal', 'resource_id'}
    extras = {
        'metric': {'metric_id', 'value', 'unit', 'temporality', 'kind'},
        'span': {'trace_id', 'span_id', 'parent_span_id', 'duration_raw', 'duration_unit'},
        'log': {'severity', 'message_available'},
    }
    for observation in data['observations']:
        signal = observation['signal']
        if signal not in extras or set(observation) != common | extras.get(signal, set()):
            errors.append('unexpected observation fields')
        if not data['start_ns'] <= observation['event_ns'] <= data['cutoff_ns']:
            errors.append('observation outside permitted window')
        oid = observation['object_id']
        if oid in by_id:
            errors.append('duplicate observation identifier')
        by_id[oid] = observation
        resource = observation['resource_id']
        if not resource.startswith('resource:') or len(resource) != 73:
            errors.append('resource identity is not opaque token')
        graph.add_node(resource, node_type='RESOURCE')
        if signal == 'span':
            spans.setdefault((observation['trace_id'], observation['span_id']), []).append(observation)
    expected_evidence = []
    for observation in data['observations']:
        if observation['signal'] != 'span':
            continue
        parent = observation['parent_span_id']
        matches = spans.get((observation['trace_id'], parent), [])
        if not parent:
            state = 'missing_parent_or_root_unknown'
        elif parent == observation['span_id']:
            state = 'self_parent_convention_unknown'
        elif not matches:
            state = 'unresolved_parent'
        elif len(matches) > 1:
            state = 'ambiguous_parent'
        else:
            state = 'resolved_parent'
            expected_evidence.append((matches[0]['object_id'], observation['object_id']))
        trace_states[state] += 1
    actual_evidence = []
    for edge in data['edges']:
        if set(edge) != {'id', 'source', 'target', 'relation', 'evidence', 'epistemic_status'}:
            errors.append('unexpected edge fields')
        support = [by_id.get(oid) for oid in edge['evidence']]
        if len(support) != 2 or any(o is None or o['signal'] != 'span' for o in support):
            errors.append('missing supporting spans')
            continue
        parent, child = support
        if (parent['resource_id'], child['resource_id']) != (edge['source'], edge['target']):
            errors.append('edge resource endpoints disagree with evidence')
        if parent['trace_id'] != child['trace_id'] or parent['span_id'] != child['parent_span_id']:
            errors.append('edge is not a supported same-trace parent relationship')
        if edge['relation'] != 'CALLS' or edge['epistemic_status'] != 'OBSERVED':
            errors.append('unsupported relation type or epistemic status')
        actual_evidence.append(tuple(edge['evidence']))
        graph.add_edge(edge['source'], edge['target'], key=edge['id'], **edge)
    if Counter(actual_evidence) != Counter(expected_evidence):
        errors.append('resolved parent and emitted edge conservation failed')
    if dict(trace_states) != data['trace_states']:
        errors.append('trace state counts disagree with independent reconstruction')
    return errors, graph


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    run = Path(args.run)
    output = Path(args.output)
    if output.exists():
        raise FileExistsError(output)
    preflight = json.loads((run / 'preflight.json').read_text())
    summary = json.loads((run / 'summary.json').read_text())
    labels = json.loads((run / 'evaluation-labels.json').read_text())
    replays = json.loads((run / 'replay-comparison.json').read_text())['passes']
    profiles = [json.loads(p.read_text()) for p in sorted(run.glob('file-*.json'))]
    records, errors = [], []
    if len(profiles) != 162 or len(labels) != 335 or len(replays) != 2:
        errors.append('expected full-file/all-annotation/two-replay population not present')
    if not all(p['crc_eof_verified'] and p['row_conservation'] for p in profiles):
        errors.append('incomplete EOF or row conservation evidence')
    if replays[0] != replays[1]:
        errors.append('replayed summaries are not identical')
    for repetition, case_rows in enumerate(replays, 1):
        for label, expected in zip(labels, case_rows, strict=True):
            name = expected['handle'].replace(':', '-') + '.json.gz'
            with gzip.open(run / 'cases' / f'replay-{repetition:03d}' / name, 'rt', encoding='utf-8') as f:
                payload = json.load(f)
            failures, graph = verify_projection(payload)
            if payload['cutoff_ns'] != label['fault_ns']:
                failures.append('case cutoff does not match declared input')
            if digest(payload) != expected['canonical_sha256'] or digest(payload['edges']) != expected['graph_sha256']:
                failures.append('saved payload does not match reported hashes')
            root_token = 'resource:' + digest(['resource', [label['scenario'], label['raw']['component']]])
            records.append({'incident_id': label['incident_id'], 'repetition': repetition,
                            'nodes': graph.number_of_nodes(), 'edges': graph.number_of_edges(),
                            'root_is_node': root_token in graph, 'failures': failures})
            errors.extend(failures)
    historical_changes = [name for name, h in preflight['historical_hashes'].items() if not Path(name).exists() or sha(Path(name)) != h]
    source_changes = [name for name, h in preflight['source_hashes'].items() if not Path(name).exists() or sha(Path(name)) != h]
    manifest = json.loads((run / 'artifact-manifest.json').read_text())
    artifact_changes = [name for name, details in manifest.items() if not (run / name).exists() or sha(run / name) != details['sha256']]
    report = {'audit_version': 'independent-e003-am002-v1', 'source_sha256': sha(Path(__file__)),
              'mechanical_summary': summary, 'cases_verified': len(records),
              'root_node_cases_before_cutoff': sum(r['root_is_node'] for r in records if r['repetition'] == 1),
              'independent_projection_errors': dict(Counter(errors)), 'historical_changes': historical_changes,
              'executed_source_changes': source_changes, 'artifact_changes': artifact_changes,
              'complete_file_profiles': len(profiles),
              'all_profiles_crc_eof_verified': all(p['crc_eof_verified'] for p in profiles),
              'all_profiles_rows_conserved': all(p['row_conservation'] for p in profiles),
              'passed': not (errors or historical_changes or source_changes or artifact_changes), 'cases': records}
    with output.open('x', encoding='utf-8') as f:
        json.dump(report, f, indent=2, sort_keys=True)
        f.write('\n')
    print(json.dumps({k: v for k, v in report.items() if k not in {'cases', 'mechanical_summary'}}, indent=2))


if __name__ == '__main__':
    main()
