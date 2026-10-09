"""Approved photographic targets, not raw-camera Kelvin, on the shared clock."""
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1]/'scripts/seasons/export_wb.py'
KNOTS = [0, 1, 2, 3, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 11, 12]


class ExportWarmthTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.exists(), 'approved warmth exporter missing')
        spec = importlib.util.spec_from_file_location('export_wb', SCRIPT)
        self.export = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.export)

    def test_targets_hit_anchors_and_wrap(self):
        values = [0., .2, .8, .1]
        for key, value in zip([0, 3, 6, 9, 12], [*values, values[0]]):
            self.assertEqual(self.export.interpolate_target(key, KNOTS, values), value)
        self.assertAlmostEqual(self.export.interpolate_target(11, KNOTS, values), .025)

    def test_interpolation_uses_elapsed_segments_not_numeric_phase(self):
        self.assertAlmostEqual(self.export.interpolate_target(5, KNOTS, [0., .2, .8, .1]), .56)
        self.assertAlmostEqual(self.export.interpolate_target(4.5, KNOTS, [0., .2, .8, .1]), .44)

    def test_invalid_timeline_and_targets_fail_closed(self):
        for key, knots, values in [(-1, KNOTS, [0]*4), (2.5, KNOTS, [0]*4),
                                    (3, [0, 3, 3, 6, 9, 12], [0]*4),
                                    (3, KNOTS, [0, 1, float('nan'), 0]),
                                    (3, KNOTS, [0]*3), (3, [0, 3, 6, 12], [0]*4)]:
            with self.assertRaises(ValueError):
                self.export.interpolate_target(key, knots, values)

    def recipe(self, view, held_phase=None, unchanged=False, reason=None):
        return {'patches': {view: [[0, 0, 2, 2]]*3}, 'photos': {
            f'{view}-{phase:02d}': dict(target_log_rb=None if unchanged else .2,
                status='HOLD' if phase == held_phase else 'owner-review-pending',
                unchanged_source=unchanged,
                hold_reasons=[reason or 'More than2% newly clipped pixels; highlight review required'] if phase == held_phase else [])
            for phase in (3, 6, 9)}}

    def test_only_exact_owner_reviewed_clipping_holds_are_allowed(self):
        recipes = {'a': self.recipe('37', 6), 'b': self.recipe('36', 3),
                   'c': self.recipe('17', 6, True), 'd': self.recipe('18', 6)}
        self.assertEqual(set(self.export.select_photos(recipes)), {'37', '36'})
        self.assertEqual(self.export.select_photos({'a': self.recipe('37', 6, reason='Reference invalid')}), {})

    def test_missing_or_duplicate_anchors_fail(self):
        r = self.recipe('21')
        del r['photos']['21-09']
        with self.assertRaises(ValueError):
            self.export.select_photos({'a': r})
        with self.assertRaises(ValueError):
            self.export.select_photos({'a': self.recipe('21'), 'b': self.recipe('21')})

    def test_candidate_report_cannot_omit_approved_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            e = self.export
            e.OUT = Path(tmp)
            e.FOLDERS = ('a',)
            (e.OUT/'source').mkdir()
            (e.OUT/'recipes/a').mkdir(parents=True)
            (e.OUT/'source/frames.json').write_text(json.dumps({'photos': {'21': {'keys': [0, 3, 6, 9], 'original': [0]}}}))
            (e.OUT/'recipes/a/recipe.json').write_text(json.dumps(self.recipe('21')))
            (e.OUT/'inputs.json').write_text('{}')
            report = dict(processor_sha256=e.digest(SCRIPT), inputs_sha256=e.digest(e.OUT/'inputs.json'), outputs={}, frames={})
            with self.assertRaisesRegex(ValueError, 'scope'):
                e.verify_candidates({'source': {}}, report)

    def test_check_does_not_create_snapshot(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.export.OUT = Path(tmp)/'output'
            self.export.REVIEWS = Path(tmp)/'missing-reviews'
            with patch.object(sys, 'argv', ['export_wb.py', '--check']):
                try:
                    self.export.run()
                except (ValueError, FileNotFoundError):
                    pass
            self.assertFalse(self.export.OUT.exists(), '--check created snapshot directory')

    def test_generated_scope_skips_original_keys_and_other_photos(self):
        manifest = {'photos': {'21': {'keys': [0, 3, 6, 9], 'original': [0]},
                               '5': {'keys': [0, 3, 6, 9]}, '17': {'keys': [0, 3, 6, 9]}}}
        self.assertEqual(list(self.export.jobs(manifest, {'21': None, '05': None})),
                         [('21', 3), ('21', 6), ('21', 9), ('05', 0), ('05', 3), ('05', 6), ('05', 9)])


if __name__ == '__main__':
    unittest.main()
