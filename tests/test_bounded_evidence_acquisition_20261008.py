"""Synthetic safety tests; fixtures are not research observations."""
import importlib.util
import json
from pathlib import Path
import unittest
import zlib

SPEC = importlib.util.spec_from_file_location('bounded_acquisition', Path(__file__).resolve().parents[1] / 'scripts/inspect_retained_sample_20261008.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class AcquisitionBoundaryTests(unittest.TestCase):
    def profiles(self):
        return [dict(scenario=s, source_key=s + str(i), path=s + '/telemetry/2020_01_01/metric/file' + str(i) + '.csv', metric_counts={'z': 4, 'a': 1, 'b': 2, 'c': 3}, selected_scale='s') for s in ['Bank', 'Market/cloudbed-1', 'Market/cloudbed-2', 'Telecom'] for i in range(3)]

    def test_selection_stays_in_each_scenario_and_caps_sources(self):
        selected = MODULE.choose(self.profiles())
        self.assertEqual(len(selected), 8)
        self.assertEqual({s: sum(p['scenario'] == s for p in selected) for s in {p['scenario'] for p in selected}}, {'Bank': 2, 'Market/cloudbed-1': 2, 'Market/cloudbed-2': 2, 'Telecom': 2})
        self.assertTrue(all(p['source_path'].startswith(p['scenario'] + '/') for p in selected))

    def test_selection_ignores_counts_labels_and_input_order(self):
        profiles = self.profiles()
        expected = MODULE.choose(profiles)
        for p in profiles:
            p['metric_counts'] = {k: 9999 for k in p['metric_counts']}
            p['fault_label'] = 'synthetic unrelated field'
        self.assertEqual(MODULE.choose(list(reversed(profiles))), expected)

    def test_valid_block_preserves_rows(self):
        rows = [[1, 2, 'mapped', None, {'value': '3'}]]
        self.assertEqual(MODULE.bounded_inflate(zlib.compress(json.dumps(rows).encode())), rows)

    def test_rejects_excess_rows_and_non_list(self):
        for rows in ([None] * 1025, {'not': 'rows'}):
            with self.assertRaises(ValueError):
                MODULE.bounded_inflate(zlib.compress(json.dumps(rows).encode()))

    def test_rejects_compressed_and_expansion_caps(self):
        for payload in (b'x' * (2 * 1024 * 1024 + 1), zlib.compress(b' ' * (8 * 1024 * 1024 + 1))):
            with self.assertRaises(ValueError):
                MODULE.bounded_inflate(payload)

    def test_rejects_trailing_or_incomplete_stream(self):
        payload = zlib.compress(b'[]')
        for bad in (payload + b'extra', payload[:-1]):
            with self.assertRaises(ValueError):
                MODULE.bounded_inflate(bad)


if __name__ == '__main__':
    unittest.main()
