"""One controlled E003-AM002 recovery, using only preserved V004 evidence."""
import argparse
from collections import Counter
from datetime import datetime, timezone
import gzip
import json
from pathlib import Path
import platform
import shutil
import sqlite3
import subprocess
import sys
import time
import traceback
import zipfile

from ..domain import canonical_json, digest
from ..inspection import file_hash
from ..representation_v2.audit import write_new, peak_memory_bytes
from .compact import projected_context_rows
from .projection import query_projection, projection_violations
from .recovery_run import fingerprint_tree, expected_windows, read_gzip_payload, write_gzip_payload

BASE = Path('experiments/E003_domain_model_adequacy/qualification/2026-10-04')


def summary_of(payload, handle):
    return {'handle': handle, 'canonical_sha256': digest(payload),
            'graph_sha256': digest(payload['edges']),
            'observations': len(payload['observations']), 'edges': len(payload['edges']),
            'trace_states': payload['trace_states'], 'violations': projection_violations(payload)}


def validate_window(payload, window):
    if set(payload) != {'observations', 'edges', 'trace_states', 'start_ns', 'cutoff_ns'}:
        raise ValueError('unexpected projection schema')
    if (payload['start_ns'], payload['cutoff_ns']) != (window['start_ns'], window['fault_ns']):
        raise ValueError('window boundaries disagree with preserved query')
    errors = projection_violations(payload)
    if errors:
        raise ValueError('projection validation: ' + str(errors[:10]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    repo = Path.cwd().resolve()
    output = Path(args.output).resolve()
    if output.exists():
        raise FileExistsError('refusing existing output')
    output.mkdir(parents=True)
    for directory in ('profiles', 'cases/replay-001', 'cases/replay-002', 'logs'):
        (output / directory).mkdir(parents=True)
    phase, affected = 'preflight', None
    started = time.perf_counter()
    counts = {'profiles': 0, 'inherited_replay1': 0, 'reconstructed_replay1': 0,
              'verified_replay1': 0, 'completed_replay2': 0}
    before, db = {}, None

    def emit(**details):
        event = {'timestamp_utc': datetime.now(timezone.utc).isoformat(), 'phase': phase, **details}
        print(json.dumps(event), flush=True)
        with (output / 'logs/execution.jsonl').open('a', encoding='utf-8') as stream:
            stream.write(json.dumps(event) + '\n')

    def guard(growth=0):
        free = shutil.disk_usage(output).free
        if free < 6442450944 + growth:
            raise RuntimeError(f'disk safety floor: {free} free, {growth} requested')
        return free

    def build(window):
        return query_projection(projected_context_rows(db, window['scenario'], window['start_ns'], window['fault_ns']),
                                window['start_ns'], window['fault_ns'])

    try:
        guard(12 * 1024**3)
        parents = {name: (BASE / 'results' / name).resolve() for name in ('V002', 'V004', 'V005')}
        before = {name: fingerprint_tree(path) for name, path in parents.items()}
        parent = parents['V004']
        parent_preflight = json.loads((parent / 'preflight.json').read_text())
        config = parent_preflight['configuration']
        if config != json.loads((BASE / 'continuation-V004/configuration.json').read_text()):
            raise ValueError('preserved V004 configuration mismatch')
        if config['replay_repetitions'] != 2 or config['incident_before_seconds'] != 300:
            raise ValueError('unexpected frozen replay parameters')
        for relative in ('src/dce_foundation/qualification/compact.py', 'src/dce_foundation/qualification/projection.py'):
            if file_hash(repo / relative) != parent_preflight['source_hashes'][relative]:
                raise ValueError('frozen projection source mismatch: ' + relative)
        snapshot_files = list((repo / 'src/dce_foundation').rglob('*.py')) + [
            repo / 'scripts/audit_e003_v006.py', repo / BASE / 'V006-recovery.md',
            repo / BASE / 'continuation-V006/configuration.json']
        with zipfile.ZipFile(output / 'source-snapshot.zip', 'x', zipfile.ZIP_DEFLATED) as archive:
            for path in snapshot_files:
                archive.write(path, path.relative_to(repo).as_posix())
        write_new(output / 'preflight.json', {'run_id': 'E003-AM002-V006', 'parent_run': 'V004',
            'created_at_utc': datetime.now(timezone.utc).isoformat(), 'configuration': config,
            'recovery_configuration': json.loads((BASE / 'continuation-V006/configuration.json').read_text()),
            'parent_fingerprints': before, 'source_hashes': {str(p.relative_to(repo)): file_hash(p) for p in snapshot_files},
            'source_snapshot_sha256': file_hash(output / 'source-snapshot.zip'),
            'python': sys.version, 'executable': sys.executable, 'platform': platform.platform(),
            'processor': platform.processor(), 'cpu_count': __import__('os').cpu_count(),
            'dependencies': subprocess.check_output([sys.executable, '-m', 'pip', 'freeze'], text=True).splitlines(),
            'git_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
            'random_seed': None, 'raw_dataset_accessed': False, 'free_bytes': guard()})
        emit(message='parent fingerprints and frozen replay configuration verified')
        labels = json.loads((parent / 'evaluation-labels.json').read_text())
        windows = expected_windows(labels, config['incident_before_seconds'])
        profiles = [json.loads(p.read_text()) for p in sorted(parent.glob('file-*.json'))]
        if len(profiles) != 162 or len(windows) != 335 or len({p['source_key'] for p in profiles}) != 162:
            raise ValueError('source/profile/window count mismatch')
        db = sqlite3.connect((parent / 'context.sqlite').as_uri() + '?mode=ro', uri=True)
        db.execute('PRAGMA query_only=ON')
        if db.execute('PRAGMA quick_check').fetchone()[0] != 'ok':
            raise ValueError('V004 context integrity check failed')
        catalog = {key: json.loads(report) for key, report in db.execute('SELECT source_key,report FROM sources')}
        if catalog != {p['source_key']: p for p in profiles}:
            raise ValueError('profile/context catalog mismatch')
        row_counts = dict(db.execute('SELECT source_key,sum(records) FROM blocks GROUP BY source_key'))
        if set(row_counts) - set(catalog):
            raise ValueError('context has uncatalogued source blocks')
        for p in profiles:
            expected = sum(p['selection_counts'].get(s, 0) for s in ('mapped','rejected','ambiguous','out_of_window','unsupported'))
            if row_counts.get(p['source_key'], 0) != expected or not p['crc_eof_verified'] or not p['row_conservation']:
                raise ValueError('profile conservation/EOF failure: ' + p['path'])
        inherited = json.loads((parent / 'inherited-complete-files.json').read_text())
        if len(inherited) != 77:
            raise ValueError('V002 inherited lineage mismatch')
        for item in inherited:
            if file_hash(Path(item['source_profile'])) != item['source_profile_sha256']:
                raise ValueError('V002 inherited profile hash mismatch')
        for source in sorted(parent.glob('file-*.json')):
            shutil.copyfile(source, output / 'profiles' / source.name)
        counts['profiles'] = 162
        for name in ('evaluation-labels.json','evaluation-queries.json','evaluation-query-associations.json',
                     'evaluation-incident-coverage.json','metric-qualification-registry.json','continuation-provenance.json'):
            shutil.copyfile(parent / name, output / name)
        write_new(output / 'context-reference.json', {'path': str(parent / 'context.sqlite'),
            'sha256': before['V004']['context.sqlite']['sha256'], 'sqlite_mode': 'ro',
            'source_profiles': 162, 'raw_dataset_rescanned': False})
        phase = 'validate_parent_replay1'
        existing = {p.name: p for p in (parent / 'cases/replay-001').glob('*')}
        expected_names = {w['expected_filename'] for w in windows.values()}
        if set(existing) - expected_names:
            raise ValueError('unexpected parent replay files')
        inventory, summaries1, classifications = [], [], Counter()
        for i, window in enumerate(windows.values(), 1):
            guard()
            affected = window['window_identity']
            source = existing.get(window['expected_filename'])
            status, summary = 'MISSING', None
            item = {**window, 'source_profile_identities': [p['source_key'] for p in profiles if p['scenario'] == window['scenario']]}
            if source is not None:
                item.update(parent_artifact=str(source), parent_sha256=file_hash(source), parent_bytes=source.stat().st_size)
                try:
                    payload = read_gzip_payload(source)
                    validate_window(payload, window)
                    summary = summary_of(payload, affected)
                    status = 'VALID'
                except (OSError, EOFError, ValueError, KeyError, __import__('zlib').error) as error:
                    status = 'CORRUPT'
                    item['parent_error'] = str(error)
            classifications[status] += 1
            item['original_status'] = status
            if status == 'VALID':
                item.update(artifact_path=str(source), artifact_sha256=item['parent_sha256'],
                            canonical_sha256=summary['canonical_sha256'], origin='V004')
            inventory.append(item)
            summaries1.append(summary)
            if i % 10 == 0 or i == 335:
                emit(checked=i, classification=dict(classifications))
        if dict(classifications) != {'VALID': 164, 'CORRUPT': 1, 'MISSING': 170}:
            raise ValueError('parent replay classification mismatch: ' + str(classifications))
        counts['inherited_replay1'] = 164
        write_new(output / 'parent-replay1-inventory.json', inventory)
        write_new(output / 'reconstruction-set.json', [item for item in inventory if item['original_status'] != 'VALID'])
        phase = 'reconstruct_replay1'
        for i, item in enumerate(inventory):
            if item['original_status'] == 'VALID':
                continue
            guard()
            affected = item['window_identity']
            payload = build(item)
            validate_window(payload, item)
            summary = summary_of(payload, affected)
            target = output / 'cases/replay-001' / item['expected_filename']
            guard(len(canonical_json(payload).encode()))
            write_gzip_payload(target, payload)
            summaries1[i] = summary
            item.update(artifact_path=str(target), artifact_sha256=file_hash(target),
                        canonical_sha256=summary['canonical_sha256'], origin='V006')
            counts['reconstructed_replay1'] += 1
            emit(completed=counts['reconstructed_replay1'], total=171, window=affected)
            del payload
        phase = 'verify_replay1'
        for i, item in enumerate(inventory):
            guard()
            affected = item['window_identity']
            payload = read_gzip_payload(Path(item['artifact_path']))
            validate_window(payload, item)
            if summary_of(payload, affected) != summaries1[i] or file_hash(Path(item['artifact_path'])) != item['artifact_sha256']:
                raise ValueError('replay1 verification mismatch')
            counts['verified_replay1'] += 1
            if counts['verified_replay1'] % 10 == 0:
                emit(verified=counts['verified_replay1'])
        write_new(output / 'replay1-inventory.json', {'expected_windows':335,'inherited_valid':164,
            'corrupt_from_v004':1,'missing_from_v004':170,'reconstructed':171,'verified':335,'windows':inventory})
        emit(verified=335, gate='PASS')
        phase = 'replay2'
        summaries2 = []
        for item in inventory:
            guard()
            affected = item['window_identity']
            payload = build(item)
            validate_window(payload, item)
            summary = summary_of(payload, affected)
            target = output / 'cases/replay-002' / item['expected_filename']
            guard(len(canonical_json(payload).encode()))
            write_gzip_payload(target, payload)
            summaries2.append(summary)
            counts['completed_replay2'] += 1
            emit(completed=counts['completed_replay2'], total=335, window=affected)
            del payload
        db.close()
        db = None
        if summaries1 != summaries2:
            raise ValueError('independent replay hash comparison failed')
        write_new(output / 'replay-comparison.json', {'equal':True,'passes':[summaries1,summaries2]})
        phase = 'independent_audit'
        audit = subprocess.run([sys.executable, 'scripts/audit_e003_v006.py', '--run', str(output)],
                               capture_output=True, text=True)
        write_new(output / 'logs/independent-audit-stdout.log', audit.stdout)
        write_new(output / 'logs/independent-audit-stderr.log', audit.stderr)
        if audit.returncode:
            raise RuntimeError('independent audit failed: ' + audit.stderr[-2000:])
        independent = json.loads((output / 'independent-audit.json').read_text())
        if not independent['passed']:
            raise ValueError('independent audit reported failure')
        phase = 'finalize'
        after = {name: fingerprint_tree(path) for name, path in parents.items()}
        if before != after:
            raise ValueError('preserved parent evidence changed')
        write_new(output / 'parent-integrity.json', {'before':before,'after':after,'unchanged':True})
        links = json.loads((output / 'evaluation-query-associations.json').read_text())
        coverage = json.loads((output / 'evaluation-incident-coverage.json').read_text())
        metrics = json.loads((output / 'metric-qualification-registry.json').read_text())
        gates = {'A':'PASS' if all(p['decision']=='QUALIFIED' and p['row_conservation'] for p in profiles) else 'FAIL',
                 'B':'NOT RETESTED; inherited V004 timestamp census',
                 'C':'PASS' if not any(s['violations'] for s in summaries1) else 'FAIL',
                 'D':'NOT RETESTED; inherited source/projection provenance',
                 'E':'PASS' if all(e['status']=='UNKNOWN' and e['evidence_source'] is None and e['confidence']==0 for e in metrics) else 'FAIL',
                 'F':'PASS' if len(coverage)==335 else 'FAIL', 'G':'PASS' if not any(s['violations'] for s in summaries1) else 'FAIL', 'H':'PASS'}
        summary = {'run_id':'E003-AM002-V006','validation_id':'V006','parent_run':'V004','recovery_status':'Completed',
            'v004_status':'Interrupted during Replay 1; preserved unchanged.', 'inherited_profiles':162,'inherited_v002_profiles':77,
            'replay1':{'inherited_valid':164,'reconstructed':171,'verified':335}, 'replay2':{'completed':335,'verified':335},
            'repeatable':True,'independent_audit_passed':True,'gates':gates,'review_required':True,
            'scientific_decision_proposal':'REVISE / restricted downstream readiness; review pending',
            'total_source_rows':sum(p['counts']['rows_seen'] for p in profiles),
            'scenario_profile_counts':dict(Counter(p['scenario'] for p in profiles)),
            'root_observed_cases':sum(c['root_observation_found'] for c in coverage),
            'before_only_root_observed_cases':sum(c['before_only_task_eligible'] for c in coverage),
            'qualified_query_associations':sum(q['status']=='QUALIFIED' for q in links),
            'unknown_query_associations':sum(q['status']=='UNKNOWN' for q in links),
            'unknown_metric_entries':sum(e['status']=='UNKNOWN' for e in metrics),
            'v002_modified':False,'v004_modified':False,'v005_modified':False,'dataset_rescanned':False,
            'elapsed_seconds':time.perf_counter()-started,'peak_memory_bytes':peak_memory_bytes(),'free_disk_bytes':guard()}
        write_new(output / 'summary.json', summary)
        write_new(output / 'results.json', {'summary':summary,'coverage':coverage,'query_limitations':[q for q in links if q['status']!='QUALIFIED']})
        write_new(output / 'decision.md', '# E003-AM002 V006 decision proposal\n\nExecution recovery completed: 162 profiles; 335/335 Replay 1 and Replay 2; identical canonical/graph hashes; independent audit passed.\n\nProposal: REVISE / restricted downstream readiness, human review pending. UNKNOWN metric semantics and unresolved query associations restrict feature/evaluator readiness. The recovery does not demonstrate RCA accuracy, hybrid superiority or causality. A/H recovery evidence does not retrospectively qualify untested B/D scientific conditions.\n\nRead summary.json and results.json for measured root coverage and query exclusions. Preserved V002/V004/V005 hashes match before/after. No dataset rescan. Stop for human review.\n')
        emit(message='technical recovery and independent verification completed', counts=counts)
        files = {str(p.relative_to(output).as_posix()):{'sha256':file_hash(p),'bytes':p.stat().st_size}
                 for p in sorted(output.rglob('*')) if p.is_file()}
        write_new(output / 'artifact-manifest.json', {'parent_run':'V004','recovery_status':'Completed',
            'v004_status':summary['v004_status'],'replay1_coverage':'335/335','replay2_status':'335/335 verified',
            'external_replay1_references': [i for i in inventory if i['origin']=='V004'], 'files':files})
    except Exception as error:
        traceback.print_exc()
        if db:
            db.close()
        unchanged = {name: fingerprint_tree(BASE / 'results' / name) == before[name] for name in before}
        write_new(output / 'failure.json', {'phase':phase,'timestamp_utc':datetime.now(timezone.utc).isoformat(),
            'error':str(error),'affected_artifact_or_window':affected,'completed_work':counts,
            'remaining_replay1':335-counts['verified_replay1'],'remaining_replay2':335-counts['completed_replay2'],
            'parent_run':'V004','recovery_run':'V006','storage_free_bytes':shutil.disk_usage(output).free,
            'parents_unchanged':unchanged,'dataset_rescanned':False,'review_required':True})
        raise


if __name__ == '__main__':
    main()
