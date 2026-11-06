import gzip
import json
from pathlib import Path
import subprocess
import sys

from scripts.validate_e003_am002 import digest, verify_projection


def payload():
    return {'start_ns': 0, 'cutoff_ns': 1, 'edges': [], 'trace_states': {},
            'observations': [{'object_id': 'observation:x', 'event_ns': 1, 'signal': 'log',
                              'resource_id': 'resource:' + 'a' * 64,
                              'severity': 'UNKNOWN', 'message_available': True}]}


def test_independent_verifier_excludes_names_and_future():
    data = payload()
    assert not verify_projection(data)[0]
    data['observations'][0]['root_entity'] = 'answer'
    data['observations'][0]['event_ns'] = 2
    errors, _ = verify_projection(data)
    assert 'unexpected observation fields' in errors
    assert 'observation outside permitted window' in errors


def test_finalizer_refuses_unfinished_run(tmp_path):
    run = tmp_path / 'unfinished'
    run.mkdir()
    review = tmp_path / 'review'
    result = subprocess.run([sys.executable, 'scripts/finalize_e003_am002.py', '--run', str(run),
                             '--review-output', str(review)], capture_output=True, text=True)
    assert result.returncode != 0
    assert 'run is not complete' in result.stderr
    assert not review.exists()


def test_complete_fixture_creates_review_without_selfapproval(tmp_path):
    run = tmp_path / 'run'
    run.mkdir()

    def put(name, obj):
        (run / name).write_text(json.dumps(obj), encoding='utf-8')

    data = payload()
    entry = {'handle': 'context:fixture', 'canonical_sha256': digest(data), 'graph_sha256': digest([])}
    for repetition in (1, 2):
        folder = run / 'cases' / f'replay-{repetition:03d}'
        folder.mkdir(parents=True)
        with gzip.open(folder / 'context-fixture.json.gz', 'wt', encoding='utf-8') as f:
            json.dump(data, f)
    labels = [{'incident_id': f'fixture-{i}', 'scenario': 'Bank', 'fault_ns': 1,
               'raw': {'component': 'fixture'}} for i in range(335)]
    put('preflight.json', {'historical_hashes': {}, 'source_hashes': {}})
    put('evaluation-labels.json', labels)
    put('replay-comparison.json', {'equal': True, 'passes': [[entry] * 335, [entry] * 335]})
    for i in range(162):
        put(f'file-{i:03d}.json', {'crc_eof_verified': True, 'row_conservation': True,
                                'scenario': 'Bank', 'path': f'fixture-{i}', 'decision': 'QUALIFIED',
                                'selected_scale': 's', 'selection_counts': {'mapped': 1},
                                'counts': {'rows_seen': 1}})
    put('summary.json', {'representation_passed': True, 'historical_records_unchanged': True,
                         'files': 162, 'total_source_rows': 162, 'labels': 335, 'queries': 335,
                         'root_observed_cases': 0, 'before_only_root_observed_cases': 0,
                         'unknown_metric_entries': 1, 'qualified_query_associations': 333,
                         'elapsed_seconds': 1, 'peak_memory_bytes': 1, 'context_store_bytes': 1,
                         'gates': {k: 'PASS' for k in 'ABCDEFGH'}})
    put('evaluation-incident-coverage.json', [{'scenario': 'Bank', 'root_observation_found': False,
                                             'before_only_task_eligible': False, 'root_trace_found': False,
                                             'query_association': 'UNKNOWN', 'coverage_status': 'OTHER_TELEMETRY_ONLY'}] * 335)
    put('metric-qualification-registry.json', [{'status': 'UNKNOWN'}])
    # Empty manifest is only a report-rendering fixture, not production provenance.
    put('artifact-manifest.json', {})
    review = tmp_path / 'review'
    result = subprocess.run([sys.executable, 'scripts/finalize_e003_am002.py', '--run', str(run),
                             '--review-output', str(review)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    facts = json.loads((review / 'results.json').read_text())
    assert facts['human_review_required']
    assert not facts['automatic_downstream_execution']
    assert 'RESTRICTED' in facts['outcome_proposal']
    assert 'not human approval' in (review / 'decision.md').read_text()
