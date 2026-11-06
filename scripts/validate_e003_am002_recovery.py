"""Independent, read-only validation for E003-AM002 V005 recovery artifacts."""
import argparse
import gzip
import json
from pathlib import Path

from dce_foundation.domain import digest
from dce_foundation.inspection import file_hash


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    run = Path(args.run)
    result = Path(args.output)
    inventory = json.loads((run / 'replay1-inventory.json').read_text())
    summary = json.loads((run / 'summary.json').read_text())
    parent = json.loads((run / 'parent-integrity.json').read_text())
    windows = inventory['windows']
    checks = []
    checks.append(['replay1_counts', (inventory['expected_windows'], inventory['inherited_valid'], inventory['reconstructed']) == (335, 164, 171)])
    checks.append(['replay1_unique', len(windows) == 335 and len({w['window_identity'] for w in windows}) == 335])
    checks.append(['parent_unchanged', parent['v004_unchanged'] and parent['v002_unchanged']])
    checks.append(['summary', summary['replay1']['verified'] == 335 and summary['replay2']['completed'] == 335 and summary['repeatable']])
    bad = []
    for item in windows:
        path = Path(item['artifact_path'])
        try:
            with gzip.open(path, 'rb') as stream:
                payload = json.loads(stream.read())
            if file_hash(path) != item['artifact_sha256'] or digest(payload) != item['canonical_sha256']:
                bad.append(item['window_identity'])
        except Exception:
            bad.append(item['window_identity'])
    replay2 = sorted((run / 'cases/replay-002').glob('*.json.gz'))
    comparison = json.loads((run / 'replay-comparison.json').read_text())
    replay2_bad = []
    expected_names = {item['expected_filename'] for item in windows}
    expected_hashes = {item['handle']: item['canonical_sha256'] for item in comparison['passes'][1]}
    for path in replay2:
        try:
            with gzip.open(path, 'rb') as stream:
                payload = json.loads(stream.read())
            handle = path.name.removesuffix('.json.gz').replace('context-', 'context:', 1)
            if handle not in expected_hashes or digest(payload) != expected_hashes[handle]:
                replay2_bad.append(path.name)
        except Exception:
            replay2_bad.append(path.name)
    checks.append(['replay1_artifacts_readable', not bad])
    checks.append(['replay2_coverage_and_readability', len(replay2) == 335 and {path.name for path in replay2} == expected_names and not replay2_bad])
    payload = {'validation_id': 'V005-independent-audit', 'passed': all(ok for _, ok in checks),
               'checks': [{'name': name, 'passed': ok} for name, ok in checks], 'bad_replay1_windows': bad,
               'replay2_files': len(replay2), 'bad_replay2_artifacts': replay2_bad}
    result.parent.mkdir(parents=True, exist_ok=True)
    result.write_text(json.dumps(payload, indent=2, sort_keys=True) + '\n')
    if not payload['passed']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
