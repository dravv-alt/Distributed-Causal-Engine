"""E003-AM002 V005: recover interrupted V004 replay without a source re-scan."""
import argparse
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
import zipfile

from ..domain import canonical_json, digest
from ..inspection import file_hash
from ..representation_v2.audit import peak_memory_bytes, write_new
from .compact import compact_coverage, projected_context_rows
from .evaluator import associations
from .projection import projection_violations, query_projection


def now():
    return datetime.now(timezone.utc).isoformat()


def disk_guard(path, config, phase):
    free = shutil.disk_usage(path).free
    if free < config['minimum_free_disk_bytes']:
        raise RuntimeError(f'disk safety limit reached during {phase}: {free} bytes free')
    return free


def fingerprint_tree(root):
    """A deterministic, content-addressed record of a preserved parent tree."""
    return {
        path.relative_to(root).as_posix(): {
            'sha256': file_hash(path), 'bytes': path.stat().st_size
        }
        for path in sorted(root.rglob('*')) if path.is_file()
    }


def expected_windows(labels, before_seconds):
    windows = {}
    for label in labels:
        start = label['fault_ns'] - before_seconds * 10**9
        handle = 'context:' + digest([label['scenario'], start, label['fault_ns']])
        if handle in windows:
            raise ValueError(f'expected-window identity collision: {handle}')
        filename = handle.replace(':', '-') + '.json.gz'
        windows[handle] = {
            'window_identity': handle,
            'scenario': label['scenario'],
            'fault_ns': label['fault_ns'],
            'start_ns': start,
            'source_profile_identity': 'V004 context.sqlite; all 162 profiles',
            'expected_filename': filename,
        }
    return windows


def project(db, window):
    payload = query_projection(
        projected_context_rows(db, window['scenario'], window['start_ns'], window['fault_ns']),
        window['start_ns'], window['fault_ns'],
    )
    return payload, {
        'window_identity': window['window_identity'],
        'canonical_sha256': digest(payload),
        'graph_sha256': digest(payload['edges']),
        'observations': len(payload['observations']),
        'edges': len(payload['edges']),
        'trace_states': payload['trace_states'],
        'violations': projection_violations(payload),
    }


def read_gzip_payload(path):
    with gzip.open(path, 'rb') as stream:
        raw = stream.read()
    return json.loads(raw)


def write_gzip_payload(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    with gzip.GzipFile(filename=str(path), mode='xb', mtime=0) as stream:
        stream.write(canonical_json(payload).encode())


def capture_preflight(repo, output, config_path, parent, v002, config):
    minimum = config['minimum_free_disk_bytes']
    estimate = config['estimated_recovery_growth_bytes']
    free = disk_guard(output, config, 'preflight')
    if free < minimum + estimate:
        raise RuntimeError('insufficient free storage for bounded recovery estimate')
    source_files = [
        repo / 'src/dce_foundation/qualification/recovery_run.py',
        repo / 'scripts/validate_e003_am002_recovery.py',
        config_path,
        config_path.parent / 'protocol.md',
        config_path.parent / 'storage-amendment.md',
        repo / 'experiments/E003_domain_model_adequacy/qualification/2026-10-04/V005-recovery.md',
    ]
    source_hashes = {path.relative_to(repo).as_posix(): file_hash(path) for path in source_files}
    with zipfile.ZipFile(output / 'source-snapshot.zip', 'x', zipfile.ZIP_DEFLATED) as archive:
        for path in source_files:
            archive.write(path, path.relative_to(repo).as_posix())
    parent_fingerprint = fingerprint_tree(parent)
    v002_fingerprint = fingerprint_tree(v002)
    write_new(output / 'preflight.json', {
        'created_at_utc': now(),
        'run_id': 'E003-AM002-V005',
        'parent_run': 'V004',
        'source_hashes': source_hashes,
        'source_snapshot_sha256': file_hash(output / 'source-snapshot.zip'),
        'parent_v004_fingerprint_before': parent_fingerprint,
        'parent_v002_fingerprint_before': v002_fingerprint,
        'free_disk_bytes_before': free,
        'estimated_recovery_growth_bytes': estimate,
        'configuration': config,
        'python': sys.version,
        'executable': sys.executable,
        'platform': platform.platform(),
        'git_sha': subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip(),
        'git_status': subprocess.check_output(['git', 'status', '--short'], text=True).splitlines(),
        'raw_dataset_accessed': False,
    })
    return parent_fingerprint, v002_fingerprint


def failure(output, config, phase, error, completed, remaining, parent_fingerprint, v002_fingerprint):
    if (output / 'failure.json').exists():
        return
    write_new(output / 'failure.json', {
        'timestamp_utc': now(), 'phase': phase, 'error': str(error),
        'affected_artifact_or_window': getattr(error, 'window_identity', None),
        'completed_work': completed, 'remaining_work': remaining,
        'parent_run': 'V004', 'recovery_run': 'V005',
        'free_disk_bytes': shutil.disk_usage(output).free,
        'existing_evidence_modified': False,
        'v004_unchanged': fingerprint_tree(Path(config['parent_results'])) == parent_fingerprint,
        'v002_unchanged': fingerprint_tree(Path(config['v002_results'])) == v002_fingerprint,
        'raw_dataset_accessed': False,
        'result': 'BLOCKED', 'review_required': True,
    })


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    repo = Path.cwd().resolve()
    output = Path(args.output).resolve()
    config_path = Path(args.config).resolve()
    config = json.loads(config_path.read_text())
    parent = Path(config['parent_results']).resolve()
    v002 = Path(config['v002_results']).resolve()
    if output.exists():
        raise FileExistsError(f'refusing to overwrite recovery output: {output}')
    if not (parent / 'context.sqlite').is_file() or not (v002 / 'context.sqlite').is_file():
        raise RuntimeError('required preserved parent context is unavailable')
    output.mkdir(parents=True)
    started = time.perf_counter()
    parent_fingerprint = v002_fingerprint = None
    phase = 'preflight'
    try:
        parent_fingerprint, v002_fingerprint = capture_preflight(repo, output, config_path, parent, v002, config)
        labels = json.loads((parent / 'evaluation-labels.json').read_text())
        queries = json.loads((parent / 'evaluation-queries.json').read_text())
        associations_data = json.loads((parent / 'evaluation-query-associations.json').read_text())
        profiles = [json.loads(path.read_text()) for path in sorted(parent.glob('file-*.json'))]
        if len(labels) != config['expected_replay1_windows'] or len(profiles) != config['inherited_profiles']:
            raise RuntimeError('V004 evidence does not match frozen recovery counts')
        windows = expected_windows(labels, config['incident_before_seconds'])
        if len(windows) != config['expected_replay1_windows']:
            raise RuntimeError('unexpected replay-1 window count')
        for index, profile in enumerate(profiles, 1):
            write_new(output / 'profiles' / f'file-{index:03d}.json', profile)
        write_new(output / 'evaluation-labels.json', labels)
        write_new(output / 'evaluation-queries.json', queries)
        write_new(output / 'evaluation-query-associations.json', associations_data)
        db = sqlite3.connect(parent.as_uri() + '/context.sqlite?mode=ro', uri=True)
        existing = {path.name: path for path in (parent / 'cases/replay-001').glob('*.json.gz')}
        unexpected = sorted(set(existing) - {window['expected_filename'] for window in windows.values()})
        if unexpected:
            raise RuntimeError('unexpected V004 replay-1 artifacts: ' + ','.join(unexpected))
        inventory, replay1 = [], []
        phase = 'validate_replay1'
        for ordinal, window in enumerate(windows.values(), 1):
            disk_guard(output, config, phase)
            source = existing.get(window['expected_filename'])
            status, path, inherited = 'MISSING', None, False
            payload = summary = None
            if source is not None:
                try:
                    payload = read_gzip_payload(source)
                    projected, summary = project(db, window)
                    if digest(payload) != summary['canonical_sha256']:
                        status = 'CORRUPT'
                    else:
                        status, path, inherited = 'VALID', source, True
                except Exception:
                    status = 'CORRUPT'
            if summary is None:
                projected, summary = project(db, window)
            if status == 'VALID':
                artifact_path = str(path)
                artifact_hash = file_hash(path)
                artifact_bytes = path.stat().st_size
            else:
                artifact_path = None
                artifact_hash = None
                artifact_bytes = None
            inventory.append({**window, 'validation_status': status, 'artifact_path': artifact_path,
                              'artifact_sha256': artifact_hash, 'artifact_bytes': artifact_bytes,
                              'canonical_sha256': summary['canonical_sha256'],
                              'inherited_from_v004': inherited})
            replay1.append(summary)
            if ordinal % 25 == 0:
                print(json.dumps({'phase': phase, 'windows_checked': ordinal}), flush=True)
        valid = [item for item in inventory if item['validation_status'] == 'VALID']
        corrupt = [item for item in inventory if item['validation_status'] == 'CORRUPT']
        missing = [item for item in inventory if item['validation_status'] == 'MISSING']
        if (len(valid), len(corrupt), len(missing)) != (164, 1, 170):
            raise RuntimeError(f'V004 replay-1 classification mismatch: {len(valid)}/{len(corrupt)}/{len(missing)}')
        phase = 'reconstruct_replay1'
        reconstructed = 0
        for item in inventory:
            if item['validation_status'] == 'VALID':
                continue
            disk_guard(output, config, phase)
            window = windows[item['window_identity']]
            payload, summary = project(db, window)
            target = output / 'cases/replay-001' / window['expected_filename']
            write_gzip_payload(target, payload)
            item.update({'artifact_path': str(target), 'artifact_sha256': file_hash(target),
                         'artifact_bytes': target.stat().st_size,
                         'reconstruction_reason': item['validation_status'],
                         'validation_status': 'RECONSTRUCTED'})
            replay1[list(windows).index(window['window_identity'])] = summary
            reconstructed += 1
            if reconstructed % 25 == 0:
                print(json.dumps({'phase': phase, 'windows_reconstructed': reconstructed}), flush=True)
        phase = 'verify_replay1'
        if len(inventory) != 335 or len({item['window_identity'] for item in inventory}) != 335:
            raise RuntimeError('replay-1 window inventory is incomplete or non-unique')
        for item in inventory:
            artifact = Path(item['artifact_path'])
            payload = read_gzip_payload(artifact)
            if digest(payload) != replay1[list(windows).index(item['window_identity'])]['canonical_sha256']:
                raise RuntimeError('replay-1 final hash mismatch: ' + item['window_identity'])
        write_new(output / 'replay1-inventory.json', {
            'expected_windows': 335, 'inherited_valid': len(valid), 'corrupt_from_v004': len(corrupt),
            'missing_from_v004': len(missing), 'reconstructed': reconstructed, 'windows': inventory,
        })
        phase = 'replay2'
        replay2 = []
        for ordinal, window in enumerate(windows.values(), 1):
            disk_guard(output, config, phase)
            payload, summary = project(db, window)
            target = output / 'cases/replay-002' / window['expected_filename']
            write_gzip_payload(target, payload)
            replay2.append(summary)
            if ordinal % 25 == 0:
                print(json.dumps({'phase': phase, 'windows_completed': ordinal}), flush=True)
        phase = 'verify_replay2'
        replay2_paths = sorted((output / 'cases/replay-002').glob('*.json.gz'))
        if len(replay2_paths) != 335 or {path.name for path in replay2_paths} != {item['expected_filename'] for item in inventory}:
            raise RuntimeError('replay-2 artifact coverage mismatch')
        if replay1 != replay2:
            raise RuntimeError('repeatability mismatch between replay-1 and replay-2')
        write_new(output / 'replay-comparison.json', {'equal': True, 'passes': [replay1, replay2]})
        coverage = compact_coverage(db, labels, associations_data, config)
        db.close()
        phase = 'finalize'
        parent_after = fingerprint_tree(parent)
        v002_after = fingerprint_tree(v002)
        if parent_after != parent_fingerprint or v002_after != v002_fingerprint:
            raise RuntimeError('preserved parent evidence changed during recovery')
        write_new(output / 'parent-integrity.json', {
            'parent_run': 'V004', 'v004_unchanged': True, 'v002_unchanged': True,
            'v004_fingerprint_before': parent_fingerprint, 'v004_fingerprint_after': parent_after,
            'v002_fingerprint_before': v002_fingerprint, 'v002_fingerprint_after': v002_after,
            'raw_dataset_accessed': False,
        })
        summary = {
            'amendment_id': 'E003-AM002', 'validation_id': 'V005', 'parent_run': 'V004',
            'recovery_status': 'Completed', 'v004_status': 'Interrupted during Replay 1; preserved unchanged.',
            'files': 162, 'inherited_v002_profiles': 77, 'inherited_profiles': 162,
            'replay1': {'expected': 335, 'inherited_valid': 164, 'reconstructed': 171, 'verified': 335},
            'replay2': {'expected': 335, 'completed': 335}, 'repeatable': True,
            'labels': len(labels), 'queries': len(queries),
            'qualified_query_associations': sum(item['status'] == 'QUALIFIED' for item in associations_data),
            'root_observed_cases': sum(item['root_observation_found'] for item in coverage),
            'before_only_root_observed_cases': sum(item['before_only_task_eligible'] for item in coverage),
            'historical_records_unchanged': True, 'v004_unchanged': True, 'v002_unchanged': True,
            'raw_dataset_accessed': False, 'review_required': True,
            'scientific_qualification_passed': False,
            'elapsed_seconds': time.perf_counter() - started,
            'peak_memory_bytes': peak_memory_bytes(), 'free_disk_bytes_after': shutil.disk_usage(output).free,
        }
        write_new(output / 'summary.json', summary)
        write_new(output / 'results.json', {
            'technical_recovery': summary,
            'coverage': coverage,
            'scientific_interpretation': 'Technical replay recovery only; E003 scientific decision remains pending human review.',
        })
        audit = subprocess.run([
            sys.executable, 'scripts/validate_e003_am002_recovery.py', '--run', str(output),
            '--output', str(output / 'independent-audit.json'),
        ], capture_output=True, text=True)
        write_new(output / 'independent-audit-stdout.log', audit.stdout)
        write_new(output / 'independent-audit-stderr.log', audit.stderr)
        if audit.returncode:
            raise RuntimeError('independent audit failed')
        write_new(output / 'decision.md', '# V005 technical recovery decision\n\nTechnical recovery completed; this is not an E003 scientific PASS. Preserve all evidence and stop for independent audit and human review.\n')
        manifest = {path.relative_to(output).as_posix(): {'sha256': file_hash(path), 'bytes': path.stat().st_size}
                    for path in sorted(output.rglob('*')) if path.is_file() and path.name != 'artifact-manifest.json'}
        write_new(output / 'artifact-manifest.json', {
            'parent_run': 'V004', 'v004_status': summary['v004_status'], 'recovery_status': 'Completed',
            'replay1_coverage': '335/335', 'replay2_status': '335/335 completed',
            'files': manifest,
        })
        print(json.dumps({'phase': 'completed', **summary}, sort_keys=True), flush=True)
    except Exception as exc:
        if parent_fingerprint is not None:
            failure(output, config, phase, exc, 'preserved partial artifacts', 'see phase and inventory', parent_fingerprint, v002_fingerprint)
        raise


if __name__ == '__main__':
    main()
