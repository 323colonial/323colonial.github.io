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

    def test_identity_and_invalid_inputs(self):
        source = (.6, .5, .4)
        self.assertEqual(self.wb.warmth_gains(source, math.log(.6/.4)), (1., 1., 1.))
        for rgb, target in [((0, .5, .4), 0), ((float('nan'), .5, .4), 0),
                            ((.5, .4), 0), ((.5, .4, .3), float('inf'))]:
            with self.assertRaises(ValueError):
                self.wb.warmth_gains(rgb, target)


if __name__ == '__main__':
    unittest.main()
