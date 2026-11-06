"""Validation for the read-only provenance inventory; no telemetry access."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'docs/research-design/2026-11-04-source-provenance-inventory'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    data = json.loads((BASE / 'inventory.json').read_text(encoding='utf-8'))
    plan = json.loads((ROOT / data['input_sample_plan']).read_text(encoding='utf-8'))
    assert sha(ROOT / data['input_sample_plan']) == data['input_sample_plan_sha256']
    frozen = {name for source in plan['selected_sources'] for name in source['metric_names']}
    inventoried = {name for group in data['candidate_groups'] for name in group['names']}
    assert frozen == inventoried and len(frozen) == 18
    required = {'meaning', 'unit', 'kind', 'temporality', 'aggregation', 'reset_behavior', 'exporter_configuration', 'dataset_version_match', 'healthy_control', 'independent_split'}
    for group in data['candidate_groups']:
        assert group['status'] == 'NOT QUALIFIED'
        assert required <= set(group['unsupported_fields'])
    assert data['answers'] == {
        'any_sampled_metric_fully_semantically_qualified': 'NO',
        'documented_healthy_control_source': 'NO',
        'documented_independent_evaluation_population': 'NO',
    }
    assert data['detector_authorized'] is False
    assert data['successor_experiment_authorized'] is False
    print('PASS: 18 frozen names, all required unknowns retained, no advancement authorization')


if __name__ == '__main__':
    main()
