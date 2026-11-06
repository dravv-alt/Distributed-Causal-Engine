"""Additive presentation preview; never writes existing records or snapshots."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from scripts.build_research_cockpit_current import build

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'frontend/research-reader-2026-10-08/records.json'


def main():
    data = build()
    data['reader_version'] = 1
    data['verified_at'] = datetime.now(timezone.utc).isoformat()
    data['review_queue'] = ['E002-R002: review its separate REVISE proposal.', 'E004-R001: review REVISE / structural prior only. No successor is approved.']
    extras = {
        'E001': ('experiments/E001', 'Synthetic simulation', 'A reproducible baseline lets later comparisons start from a known reference.', ['experiments/E001/logs/E001-R001.md', 'docs/engineering/otlp-intake-implementation.md']),
        'E002': ('experiments/E002', 'Synthetic simulation', 'Test whether keeping onset sources consistent improves component ranking while other inputs stay fixed.', ['experiments/E002/results/E002-R001/frozen-configuration.json', 'experiments/E002/results/E002-R001/decision-proposal.md', 'experiments/E002/results/E002-R002/comparison-r001-r002.md']),
        'E003': ('experiments/E003_domain_model_adequacy', 'Real OpenRCA telemetry; representation/replay', 'Check that real evidence survives representation before interpreting it as diagnostic information.', ['experiments/E003_domain_model_adequacy/qualification/2026-10-04/protocol.md', 'experiments/E003_domain_model_adequacy/qualification/2026-10-04/configuration.json', 'experiments/E003_domain_model_adequacy/qualification/2026-10-04/run-ledger.md', 'experiments/E003_domain_model_adequacy/qualification/2026-10-04/V006-recovery.md']),
        'E004': ('experiments/E004_symbolic_rca_baseline', 'Real OpenRCA replay; retrospective ranking', 'Compare graph structure with independent count and chance references before assuming graph reasoning helps.', ['experiments/E004_symbolic_rca_baseline/protocol.md', 'experiments/E004_symbolic_rca_baseline/configuration.yaml', 'experiments/E004_symbolic_rca_baseline/results/E004-R001/run.md']),
    }
    for e in data['experiments']:
        folder, population, rationale, paths = extras[e['experiment_id']]
        e.update(population=population, rationale=rationale)
        e['documents'] = []
        for path in dict.fromkeys([folder+'/hypothesis.md', folder+'/configuration.yaml', folder+'/run.md', *paths]):
            raw = (ROOT/path).read_bytes()
            e['documents'].append({'path':path, 'sha256':hashlib.sha256(raw).hexdigest(), 'text':raw.decode('utf-8')})
    e1 = data['experiments'][0]
    e1['facts'] = [e1['facts'][0], e1['facts'][1], 'Original R0 tests: 25 passed, 1 failed, 2 errored. CLI reproduction succeeded separately.', '47 passing tests belong to a separate OTLP engineering workspace check; they do not erase the original R0 failures.']
    e1['review_provenance'] = 'User acceptance is reported by the supplied handoff and CURRENT_RESULTS.md; the linked E001 decision file is an older pending record. No dedicated E001 approval record was located in this audit.'
    data['experiments'][1]['review_provenance'] = 'R001 acceptance is reported by the handoff and CURRENT_RESULTS.md. R002 has its own pending decision proposal.'
    data['experiments'][2]['review_provenance'] = 'Dated 2026-10-06 approval accepts representation/replay infrastructure only; scientific REVISE remains.'
    data['experiments'][3]['review_provenance'] = 'Execution is complete; the run-specific decision is a proposal awaiting human review.'
    current = json.loads((ROOT/'frontend/research-cockpit/data/experiments.json').read_text(encoding='utf-8'))
    fresh = build()
    current.pop('generated_at', None)
    fresh.pop('generated_at', None)
    data['existing_snapshot_matches_builder'] = current == fresh
    sources = {a['path']: a['sha256'] for e in data['experiments'] for a in e['artifacts'] + e['documents']}
    for path, digest in sources.items():
        if hashlib.sha256((ROOT/path).read_bytes()).hexdigest() != digest:
            raise ValueError('Evidence changed during build: '+path)
    data['source_hashes'] = sources
    # Exclusive creation preserves the dated preview as well as existing records.
    with OUT.open('x', encoding='utf-8') as stream:
        json.dump(data, stream, indent=2, ensure_ascii=False)
    print(f'Added {OUT.relative_to(ROOT)}; verified {len(sources)} evidence files')


if __name__ == '__main__':
    main()
