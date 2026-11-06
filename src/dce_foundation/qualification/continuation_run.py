"""New E003 run: verified compact checkpoint inheritance, never edits V002."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import time
from . import compact_run as runner
from ..inspection import file_hash
from ..representation_v2.audit import write_new


def streamed_archive_hash(path, retries=3, block_size=1024 * 1024):
    """Hash a Google Drive streamed file without accepting a partial read.

    The digest state is retained only for bytes already read successfully.  On
    a transient Drive read failure, reopen and seek to the next unread byte;
    after the retry budget is exhausted, fail the preflight rather than trust
    an incomplete archive.
    """
    digest = hashlib.sha256()
    offset = 0
    failures = 0
    size = path.stat().st_size
    while offset < size:
        try:
            with path.open('rb') as stream:
                stream.seek(offset)
                while offset < size:
                    block = stream.read(min(block_size, size - offset))
                    if not block:
                        raise OSError('unexpected EOF while hashing '+str(path))
                    digest.update(block)
                    offset += len(block)
        except OSError as exc:
            failures += 1
            if failures > retries:
                raise RuntimeError('archive could not be read reliably after retries: '+str(path)) from exc
            print(json.dumps({'phase':'archive_hash_retry','file':str(path),
                              'offset':offset,'attempt':failures,'error':str(exc)}), flush=True)
            time.sleep(failures)
    return digest.hexdigest()


def inherit_blocks(old_path, new_db, output):
    profiles = [json.loads(p.read_text()) for p in sorted(old_path.glob('file-*.json'))]
    if len(profiles) != 77:
        raise ValueError('Expected exactly 77 completed V002 profiles')
    catalog = {p['source_key']: p for p in profiles}
    if len(catalog) != 77 or not all(p['crc_eof_verified'] and p['row_conservation'] for p in profiles):
        raise ValueError('Invalid completed checkpoint evidence')
    old = sqlite3.connect((old_path/'context.sqlite').resolve().as_uri()+'?mode=ro', uri=True)
    counts = Counter()
    for key, env, signal, a, b, n, payload in old.execute('SELECT source_key,environment,signal,min_ns,max_ns,records,payload FROM blocks ORDER BY bid'):
        if key not in catalog:
            continue  # Incomplete file blocks must be rescanned, not inherited.
        new_db.execute('INSERT INTO blocks(source_key,environment,signal,min_ns,max_ns,records,payload) VALUES (?,?,?,?,?,?,?)',
                       (key, env, signal, a, b, n, payload))
        counts[key] += n
        if counts.total() % 100000 < n:
            new_db.commit()
            if shutil.disk_usage(output).free < 6442450944:
                raise RuntimeError('Continuation import disk safety stop')
    manifest = []
    for i, profile in enumerate(profiles, 1):
        expected = sum(profile['selection_counts'].get(s, 0) for s in ('mapped','rejected','ambiguous','out_of_window','unsupported'))
        if counts[profile['source_key']] != expected:
            raise ValueError('Completed-file row conservation failed')
        original = old.execute('SELECT report FROM sources WHERE source_key=?', (profile['source_key'],)).fetchone()
        if original is None or json.loads(original[0]) != profile:
            raise ValueError('Source catalog and profile disagree')
        source = old_path/f'file-{i:03d}.json'
        new_db.execute('INSERT INTO sources VALUES (?,?,?,?,?)', (profile['source_key'], profile['scenario'], profile['path'], profile['decision'], original[0]))
        write_new(output/f'file-{i:03d}.json', profile)
        manifest.append({'source_profile':str(source), 'source_profile_sha256':file_hash(source),
                         'decompressed_sha256':profile['decompressed_sha256'], 'crc_eof_verified':True,
                         'rows_transferred':counts[profile['source_key']]})
    old.close()
    new_db.commit()
    write_new(output/'inherited-complete-files.json', manifest)
    print(json.dumps({'phase':'checkpoint_inherited','completed_files':77,'remaining_files':85}), flush=True)
    return profiles


def main():
    original_capture = runner.capture_preflight
    original_rows = runner.context_rows
    state = {}

    def capture(repo, output, config_path):
        original_capture(repo, output, config_path)
        config = json.loads(config_path.read_text())
        state.update(output=output, minimum=config['minimum_free_disk_bytes'])
        old = repo/'experiments/E003_domain_model_adequacy/qualification/2026-10-04/results/V002'
        inventory = json.loads((repo/'provenance/storage-migration/2026-10-04/source-inventory.json').read_text())
        hashes = {p['relative_repository_path']:p['source_sha256'] for p in inventory['file_list']}
        protected = {}
        for p in sorted(old.iterdir()):
            if not p.is_file():
                continue
            key = p.relative_to(repo).as_posix()
            actual = file_hash(p)
            if key not in hashes or actual != hashes[key]:
                raise ValueError('V002 rescue inventory hash mismatch: '+key)
            protected[key] = actual
        dataset = []
        manifest = json.loads((repo/'data/manifests/openrca.json').read_text())
        for archive in manifest['archives']:
            source = Path(config['dataset_root'])/Path(archive['path']).name
            print(json.dumps({'phase':'archive_hash_verification','file':str(source)}), flush=True)
            actual = streamed_archive_hash(source)
            if actual != archive['sha256']:
                raise ValueError('Dataset archive hash mismatch: '+str(source))
            dataset.append({'path':str(source),'sha256':actual,'bytes':source.stat().st_size})
        authorization = config_path.parent.parent / (config_path.parent.name.replace('continuation-', '') + '-continuation.md')
        write_new(output/'continuation-provenance.json', {'parent_run':'E003-AM002 V002 PARTIAL 77/162',
                  'parent_file_hashes':protected,'archives_verified':dataset,
                  'continuation_records':{str(p.relative_to(repo)):{'sha256':file_hash(p),'content':p.read_text()}
                      for p in (repo/'tests/test_e003_checkpoint_continuation.py',
                                authorization)},
                  'partial_file_blocks_inherited':False,'scientific_protocol_changed':False})

    def guarded_rows(*args):
        if shutil.disk_usage(state['output']).free < state['minimum']:
            raise RuntimeError('Replay disk safety limit reached')
        yield from original_rows(*args)

    runner.capture_preflight = capture
    runner.inherit_complete_files = inherit_blocks
    runner.context_rows = guarded_rows
    runner.VERSION += '-checkpoint-continuation1'
    try:
        runner.main()
    except Exception as exc:
        if 'output' in state and not (state['output']/'failure.json').exists():
            write_new(state['output']/'failure.json', {'error':str(exc),'result':'BLOCKED',
                      'completed_files':len(list(state['output'].glob('file-*.json'))),
                      'review_required':True})
        raise


if __name__ == '__main__':
    main()
