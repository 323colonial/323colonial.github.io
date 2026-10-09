"""Offline lighting-reference math; no Blender or generation calls."""
import importlib.util
import math
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location(
    'lighting_reference', Path(__file__).resolve().parents[1] / 'scripts/seasons/lighting_reference.py')
ref = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ref)


class LightingReferenceTests(unittest.TestCase):
    def test_source_colors_preserve_photopic_flux(self):
        for kelvin in (2700, 3000, 5000, 6500, 9000):
            rgb = ref.cct_rgb(kelvin)
            self.assertAlmostEqual(ref.luminance(rgb), 1, places=6)
            self.assertTrue(all(v > 0 for v in rgb))
        warm, cool = ref.cct_rgb(2700), ref.cct_rgb(5000)
        self.assertGreater(warm[0] / warm[2], cool[0] / cool[2])
        with self.assertRaises(ValueError):
            ref.cct_rgb(1000)

    def test_hard_spot_preserves_total_flux(self):
        self.assertAlmostEqual(ref.spot_fraction(math.pi), .5)
        self.assertAlmostEqual(ref.spot_fraction(math.radians(45)), .03806023374435663)
        with self.assertRaises(ValueError):
            ref.spot_fraction(0)

    def test_full_timeline_matches_manifest_and_keeps_anchor_sources(self):
        import json
        manifest = json.loads((ref.ROOT / 'assets/seasons-next/frames.json').read_text())
        self.assertEqual(list(ref.TIMELINE), manifest['knots'][:-1])
        seasons = [ref.season(k) for k in ref.TIMELINE]
        self.assertEqual(len({s['label'] for s in seasons}), 18)
        for s in seasons:
            if s['elevation'] <= 0:
                self.assertEqual(s['sun_lux_normal'], 0)
        for key, canopy, kelvin in ((0, .3, 5200), (3, .5, 3500), (9, .6, 4300)):
            s = ref.season(key)
            self.assertAlmostEqual(s['direct_canopy_factor'], canopy)
            self.assertAlmostEqual(s['sun_kelvin'], kelvin)

    def test_compass_matches_model_axes(self):
        for azimuth, expected in ((0, (0, -1, 0)), (90, (-1, 0, 0)),
                                  (180, (0, 1, 0)), (270, (1, 0, 0))):
            for actual, wanted in zip(ref.sun_direction(azimuth, 0), expected):
                self.assertAlmostEqual(actual, wanted)
        self.assertAlmostEqual(ref.sun_direction(0, 90)[2], 1)

    def test_season_uses_actual_original_and_dark_winter(self):
        original, fall, winter, spring = [ref.season(k) for k in (0, 3, 6, 9)]
        self.assertEqual(original['local'], '2026-10-01T10:00:00-04:00')
        self.assertTrue(25 < original['elevation'] < 35)
        self.assertTrue(80 < spring['azimuth'] < 100)
        self.assertGreater(fall['sun_lux_normal'], 0)
        self.assertEqual(winter['sun_lux_normal'], 0)
        self.assertLess(winter['sky_lux_horizontal'], .01)
        self.assertGreater(original['sky_lux_horizontal'], fall['sky_lux_horizontal'])


if __name__ == '__main__':
    unittest.main()
