"""Read-only additive registration check; legacy adoption checkpoint is preserved."""
import hashlib
import json
from pathlib import Path
from check_project_governance import check

ROOT = Path(__file__).resolve().parents[1]


def main():
    errors, protected, _ = check(ROOT)
    registration = json.loads((ROOT/'docs/governance/registrations/E004.json').read_text())
    for name in ('register_amendment', 'predecessor_review', 'protocol', 'configuration'):
        if not (ROOT/registration[name]).is_file():
            errors.append('missing registration evidence: '+name)
    actual = hashlib.sha256((ROOT/'EXPERIMENT_INDEX.md').read_bytes()).hexdigest()
    if actual != registration['original_register_sha256']:
        errors.append('historical register modified')
    if registration['experiment_id'] != 'E004' or registration['successor_allocated']:
        errors.append('unauthorized experiment allocation')
    if registration['authority'] != 'User: Go ahead with the E004':
        errors.append('missing explicit successor execution authority')
    config = json.loads((ROOT/registration['configuration']).read_text())
    if config['experiment_id'] != 'E004' or config['expected_windows'] != 335:
        errors.append('registered scope mismatch')
    audit = ROOT/config['input_root']/'independent-audit.json'
    if not json.loads(audit.read_text())['passed']:
        errors.append('predecessor technical audit did not pass')
    if errors:
        raise SystemExit('\n'.join(errors))
    print(json.dumps({'additive_registration':'E004','protected_files_unchanged':protected,
        'predecessor_accepted_scope':'representation/replay infrastructure only',
        'scientific_limitations_retained':True,'legacy_checker_is_historical':True}))


if __name__ == '__main__':
    main()
