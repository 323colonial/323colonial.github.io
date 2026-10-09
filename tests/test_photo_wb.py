"""Private photographic warm/cool axis, not camera-CCT inference."""
import importlib.util
import math
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1]/'scripts/seasons/photo_wb.py'


class PhotoWarmthTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.exists(), 'photo warmth helper missing')
        spec = importlib.util.spec_from_file_location('photo_wb', SCRIPT)
        self.wb = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.wb)

    def test_target_preserves_tint_axis_and_patch_luminance(self):
        source = (.65, .45, .30)
        target = math.log(1.4)
        gains = self.wb.warmth_gains(source, target)
        result = tuple(a*b for a, b in zip(source, gains))
        self.assertAlmostEqual(math.log(result[0]/result[2]), target)
        self.assertAlmostEqual(result[1]/math.sqrt(result[0]*result[2]),
                               source[1]/math.sqrt(source[0]*source[2]))
        self.assertAlmostEqual(self.wb.luminance(result), self.wb.luminance(source))

    def test_three_patch_median_rejects_one_color_outlier(self):
        self.assertEqual(self.wb.reference_rgb([(.6, .58, .54), (.61, .59, .55), (.3, .15, .05)]),
                         (.6, .58, .54))
        for patches in [[], [(1, 1, 1)]*2, [(1, 1, 1), (1, 1, 1), (1, float('nan'), 1)]]:
            with self.assertRaises(ValueError):
                self.wb.reference_rgb(patches)

    def test_photo_led_shifts_keep_room_variation_but_cap_night(self):
        shifts = self.wb.photo_shifts({'loft': [0, .2, 1., .1], 'great': [0, .1, .5, .05]})
        self.assertAlmostEqual(shifts['loft'][2], math.log(1.10))
        self.assertAlmostEqual(shifts['great'][2], math.log(1.10)/2)
        self.assertEqual(shifts['loft'][0], 0)
        self.assertAlmostEqual(shifts['loft'][1]/shifts['loft'][2], .2)
        with self.assertRaises(ValueError):
            self.wb.photo_shifts({'room': [0, 0, 0, 0]})

    def test_new_room_reuses_saved_global_scale(self):
        shifts = self.wb.photo_shifts({'kitchen': [0, .1, .4, .02]}, peak=2.)
        self.assertAlmostEqual(shifts['kitchen'][2], math.log(1.10)*.2)
        self.assertAlmostEqual(shifts['kitchen'][1], math.log(1.10)*.05)
        for peak in (0, -1, float('nan')):
            with self.assertRaises(ValueError):
                self.wb.photo_shifts({'kitchen': [0, .1, .4, .02]}, peak=peak)

    def test_kitchen_batch_routes_visible_great_room_separately(self):
        self.assertEqual(getattr(self.wb, 'KITCHEN_TARGETS', None),
                         {'05': 'kitchen', '35': 'great-room', '47': 'kitchen', '48': 'kitchen'})

    def test_remaining_interiors_have_complete_disjoint_room_coverage(self):
        expected = {'primary-bedroom': ('18', '37'), 'guest-bedroom': ('23', '60'),
                    'powder-room': ('36',), 'upper-bath': ('38',), 'hall': ('49',), 'mudroom': ('54',),
                    'great-room': ('34', '42', '44', '45', '46'), 'loft': ('58', '61'),
                    'back-porch': ('04', '50', '17', '51', '52', '53')}
        self.assertEqual(getattr(self.wb, 'INTERIOR_GROUPS', None), expected)
        self.assertEqual(set(self.wb.INTERIOR_MODEL_VIEWS), set(expected)-{'great-room', 'loft'})
        self.assertTrue(all(len(v)==2 for v in self.wb.INTERIOR_MODEL_VIEWS.values()))
        new_ids = [v for group in expected.values() for v in group]
        self.assertEqual(len(new_ids), len(set(new_ids)))
        for view in new_ids:
            self.assertEqual(len(self.wb.PATCHES[view]), 3)
        self.assertEqual(self.wb.HELD_INTERIORS, ('30', '73'))
        self.assertEqual(self.wb.ORIGINAL_INTERIORS, ('07', '15', '19', '20', '24', '55', '56'))

    def test_only_upper_bath_winter_uses_visible_loft_wall_reference(self):
        self.assertTrue(hasattr(self.wb, 'photo_reference'), 'doorway loft reference missing')
        patches = ((1090, 450, 40, 35), (1170, 450, 40, 35), (1140, 500, 40, 30))
        for area, views in self.wb.INTERIOR_GROUPS.items():
            for view in views:
                for phase in (3, 6, 9):
                    expected = ('loft', patches) if (view, phase) == ('38', 6) else (area, self.wb.PATCHES[view])
                    self.assertEqual(self.wb.photo_reference(view, phase, area), expected)

    def test_probe_sampling_normalizes_brightness_not_chromaticity(self):
        self.assertTrue(hasattr(self.wb, 'probe_gain'), 'HDR probe normalization missing')
        for rgb in ((100., 80., 60.), (.001, .0003, .0001)):
            gain = self.wb.probe_gain(rgb)
            result = tuple(v*gain for v in rgb)
            self.assertAlmostEqual(self.wb.luminance(result), .1)
            self.assertAlmostEqual(result[0]/result[2], rgb[0]/rgb[2])
        with self.assertRaises(ValueError):
            self.wb.probe_gain((0, 0, 0))

    def test_daybed_anchors_transfer_relative_wood_warmth_not_wood_color(self):
        self.assertTrue(hasattr(self.wb, 'wood_transfer'), 'daybed-to-wood transfer missing')
        anchors = [((.6, .3, .1), (.72, .3, .1)), ((.4, .2, .2), (.48, .2, .2))]
        self.assertAlmostEqual(self.wb.wood_transfer(anchors), math.log(1.2))
        self.assertEqual(self.wb.INTERIOR_GROUPS['back-porch'][:2], self.wb.PORCH_WHITE_ANCHORS)
        self.assertEqual(set(self.wb.PORCH_WOOD_PATCHES), set(self.wb.INTERIOR_GROUPS['back-porch']))
        for invalid in ([], anchors[:1], [((0, .2, .1), (.4, .2, .1))]*2):
            with self.assertRaises(ValueError):
                self.wb.wood_transfer(invalid)

    def test_conflicting_wood_anchors_are_held_not_averaged(self):
        for ratios in ((1., 2.), (.95, 1.05)):
            with self.assertRaisesRegex(ValueError, 'disagree'):
                self.wb.wood_transfer([((.4, .3, .2), (.4*r, .3, .2)) for r in ratios])

    def test_held_daybed_anchor_cannot_drive_transfer(self):
        pairs = [((.4, .3, .2), (.44, .3, .2))]*2
        with self.assertRaisesRegex(ValueError, 'anchor held'):
            self.wb.wood_transfer(pairs, anchor_holds=['04 reference invalid'])

    def test_zero_photo_channel_can_be_sampled_then_held(self):
        rgb = self.wb.reference_rgb([(.08, .015, 0)]*3)
        self.assertEqual(rgb, (.08, .015, 0))
        self.assertFalse(self.wb.reference_usable(rgb))

    def test_near_black_photo_reference_is_not_usable(self):
        self.assertTrue(hasattr(self.wb, 'reference_usable'), 'photo signal guard missing')
        self.assertFalse(self.wb.reference_usable((.08, .015, .00061)))
        self.assertFalse(self.wb.reference_usable((1., .99, .98)))
        self.assertTrue(self.wb.reference_usable((.6, .5, .4)))

    def test_b_keeps_photo_led_base_and_adds_relative_look_difference(self):
        base = [0., .04, .095, .016]
        result = self.wb.look_shifts(base, [.001, .01, .06, .002])
        for actual, expected in zip(result, [0., .049, .154, .017]):
            self.assertAlmostEqual(actual, expected)
        self.assertEqual(self.wb.look_shifts(base, [0.]*4), base)
        with self.assertRaises(ValueError):
            self.wb.look_shifts(base, [0., float('nan'), 0., 0.])

    def test_identity_and_invalid_inputs(self):
        source = (.6, .5, .4)
        self.assertEqual(self.wb.warmth_gains(source, math.log(.6/.4)), (1., 1., 1.))
        for rgb, target in [((0, .5, .4), 0), ((float('nan'), .5, .4), 0),
                            ((.5, .4), 0), ((.5, .4, .3), float('inf'))]:
            with self.assertRaises(ValueError):
                self.wb.warmth_gains(rgb, target)


if __name__ == '__main__':
    unittest.main()
