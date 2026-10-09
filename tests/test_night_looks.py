"""Display-only adaptation checks; no Blender required."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/seasons'))
import night_looks as looks
from lighting_reference import cct_rgb, luminance


class NightLooksTests(unittest.TestCase):
    def test_baseline_is_exact_identity(self):
        rgb = (.15, .37, .82)
        self.assertEqual(looks.transform(looks.adaptation(2700), rgb), rgb)

    def test_reference_white_maps_without_exposure_change(self):
        source = cct_rgb(2700)
        for target in (3000, 3250, 3500):
            actual = looks.transform(looks.adaptation(target), source)
            for a, b in zip(actual, cct_rgb(target)):
                self.assertAlmostEqual(a, b, places=5)
            self.assertAlmostEqual(luminance(actual), 1, places=5)

    def test_options_cool_monotonically_without_neutralizing_colors(self):
        source = cct_rgb(2700)
        ratios = []
        for target in (2700, 3000, 3250, 3500):
            matrix = looks.adaptation(target)
            white = looks.transform(matrix, source)
            ratios.append(white[0]/white[2])
            blue_paint = looks.transform(matrix, (.21, .30, .46))
            self.assertGreater(blue_paint[2], blue_paint[0])
        self.assertEqual(ratios, sorted(ratios, reverse=True))

    def test_transform_is_linear_and_rejects_invalid_temperature(self):
        matrix = looks.adaptation(3250)
        a, b = (.5, .2, .1), (.1, .4, .8)
        combined = looks.transform(matrix, tuple(x+y for x, y in zip(a, b)))
        separate = tuple(x+y for x, y in zip(looks.transform(matrix, a), looks.transform(matrix, b)))
        for x, y in zip(combined, separate):
            self.assertAlmostEqual(x, y)
        with self.assertRaises(ValueError):
            looks.adaptation(1000)


if __name__ == '__main__':
    unittest.main()
