"""New presentation snapshot from preserved evidence; refuses replacement."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'frontend/research-updates-2026-10-08/records.json'
BASE = 'docs/research-design/2026-10-08-bounded-acquisition/'


def main():
    if OUT.exists():
        raise FileExistsError('Preserve the dated frontend snapshot')
    original = ROOT / 'frontend/research-reader-2026-10-08/records.json'
    data = json.loads(original.read_text(encoding='utf-8'))
    sources = dict(data['source_hashes'])
    sources[str(original.relative_to(ROOT)).replace('\\', '/')] = hashlib.sha256(original.read_bytes()).hexdigest()

    def evidence(path, label):
        raw = (ROOT / path).read_bytes()
        digest = hashlib.sha256(raw).hexdigest()
        sources[path] = digest
        return {'path': path, 'label': label, 'sha256': digest}

    amendments = {
        'E002': 'docs/governance/amendments/2026-10-08-E002-R002-REVISE-approval.md',
        'E004': 'docs/governance/amendments/2026-10-08-E004-R001-execution-acceptance.md',
    }
    for e in data['experiments']:
        if e['experiment_id'] in amendments:
            a = evidence(amendments[e['experiment_id']], 'Human approval: 8 October 2026')
            e['artifacts'].append(a)
            e['documents'].append({**a, 'text': (ROOT / a['path']).read_text(encoding='utf-8')})
            e['status'] = 'REVISE'
            e['blocking'] = 'No successor experiment is authorized. Detector development and E005 registration/execution remain unauthorized.'
            e['review_provenance'] = 'Explicit project-user approval recorded in the separate dated amendment; original proposal remains unchanged.'
            if e['experiment_id'] == 'E002':
                e['review_status'] = 'R002 REVISE approved separately on 8 October 2026; R001 acceptance retained'
                e['waiting'] = 'Qualified environment and repeatable reproduction; no improvement from the tested timing policy. This does not rule out temporal methods generally.'
                e['history'] = ['R001: accepted REVISE; environment qualification failed.', 'R002: qualified environment; unchanged performance; separate REVISE approved on 8 October 2026.']
            else:
                e['review_status'] = 'Execution accepted on 8 October 2026; REVISE / structural prior only retained'
                e['waiting'] = 'Execution accepted. Graph ranking did not beat observation counts; no successful RCA or causal interpretation is approved.'
    paths = [('review-summary.json', 'Acquisition stopping decision'), ('retained-sample-summary.json', 'Measured sample aggregates'), ('sample-plan.json', 'Selection frozen before inspection'), ('acquisition-scope.md', 'Authorized scope and bounds'), ('evidence-acquisition-assessment.md', 'Complete acquisition report'), ('official-reference.json', 'Pinned official documentation'), ('verification.json', 'Preservation and safety verification')]
    artifacts = [evidence(BASE + p, label) for p, label in paths]
    sample = json.loads((ROOT / (BASE + 'retained-sample-summary.json')).read_text(encoding='utf-8'))
    review = json.loads((ROOT / (BASE + 'review-summary.json')).read_text(encoding='utf-8'))
    data['acquisition'] = {
        'title': 'Bounded evidence acquisition complete',
        'date': review['date'], 'totals': sample['totals'],
        'varying_series': sum(s['distinct_finite_values'] > 1 for r in sample['reports'] for s in r['series_summaries']),
        'answers': [
            {'question': 'Sufficiently qualified metric subset?', 'answer': review['metric_subset'], 'reason': 'Local units, meaning, temporality, aggregation and reset behavior remain unsupported.'},
            {'question': 'Defensible healthy controls?', 'answer': review['normal_control_source'], 'reason': 'Fault-centered retained windows do not certify healthy variation.'},
            {'question': 'Independent evaluation split?', 'answer': review['independent_evaluation_split'], 'reason': 'No untouched exposure population was identified within this scope.'},
        ],
        'sources': [{'scenario': r['scenario'], 'path': r['source_path'], 'rows': r['inspected_rows'], 'series': len(r['series_summaries']), 'observed_names': r['selected_names_observed']} for r in sample['reports']],
        'artifacts': artifacts,
        'limitations': ['27 varying series are descriptive observations, not healthy controls or detector performance.', 'Five prefixes did not contain their preselected metric names; no replacement was made. This does not establish absence from the full files.', 'Official Bank trace millisecond descriptions conflict with inherited March 23–25 seconds-scale profiles. Neither record was changed.', 'The upstream code revision is not proved to match the local dataset version. Metric-name resemblance does not establish semantics.', 'Sampled hashes and database size/mtime were checked. The historical full database checksum was not reverified.'],
        'next': 'Review whether to authorize source-owner metric definitions/exporter configuration, documented healthy controls and a separate evaluation population. Acquisition has stopped.',
        'boundary': 'No detector development, successor experiment or E005 registration/execution is authorized.',
    }
    data['review_queue'] = []
    data['current_stage'] = {'title': 'Reviews recorded; evidence prerequisites still missing', 'status': 'REVISE', 'plain': 'E004 execution and E002-R002 REVISE are approved. Bounded acquisition is complete; qualified symptoms, healthy controls and an independent evaluation split remain unestablished.'}
    data['next_action'] = data['acquisition']['next'] + ' ' + data['acquisition']['boundary']
    data['generated_at'] = data['verified_at'] = datetime.now(timezone.utc).isoformat()
    data['frontend_update_version'] = 1
    data['source_hashes'] = sources
    for path, digest in sources.items():
        if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest:
            raise ValueError('Evidence hash conflict: ' + path)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open('x', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f'New snapshot: {len(sources)} evidence hashes verified')


if __name__ == '__main__':
    main()
