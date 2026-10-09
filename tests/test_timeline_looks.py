"""Shared appearance curve checks; no Blender or image writes."""
import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/seasons'))
import timeline_looks as timeline
import night_looks as night
from lighting_reference import cct_rgb


class TimelineLooksTests(unittest.TestCase):
    def setUp(self):
        self.whites = [cct_rgb(k) for k in (5000, 6500, 4000, 2700)]

    def test_coolest_anchor_and_exact_night_treatment(self):
        for target in (3250, 3500):
            cool, weights, gains = timeline.treatments(self.whites, 3, target)
            self.assertEqual(cool, 1)
            self.assertAlmostEqual(weights[1], 0)
            self.assertAlmostEqual(weights[3], 1)
            neutral = night.transform(timeline.matrix_from_gains(gains[1]), self.whites[1])
            for value in neutral:
                self.assertAlmostEqual(value, 1, places=5)
            for actual, expected in zip(timeline.matrix_from_gains(gains[3]), night.adaptation(target)):
                for a, b in zip(actual, expected):
                    self.assertAlmostEqual(a, b, places=12)

    def test_curve_is_cyclic_continuous_and_positive(self):
        _, _, gains = timeline.treatments(self.whites, 3, 3250)
        self.assertEqual(timeline.curve(gains, 0), timeline.curve(gains, 4))
        for knot in range(4):
            exact = timeline.curve(gains, knot)
            for value, expected in zip(exact, gains[knot]):
                self.assertAlmostEqual(value, expected)
            for offset in (-1e-5, 1e-5):
                for a, b in zip(timeline.curve(gains, knot+offset), exact):
                    self.assertLess(abs(a-b), 1e-8)
        for i in range(65):
            self.assertTrue(all(math.isfinite(x) and x > 0 for x in timeline.curve(gains, i/16)))

    def test_changed_component_is_rejected(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/'component.exr'
            path.write_bytes(b'original linear component')
            expected = night.digest(path)
            self.assertEqual(timeline.verify_component(path, expected), expected)
            path.write_bytes(b'replaced component')
            with self.assertRaises(ValueError):
                timeline.verify_component(path, expected)

    def test_invalid_reference_is_rejected(self):
        with self.assertRaises(ValueError):
            timeline.treatments([(0, 1, 1), (1, 1, 1)], 1, 3250)
        with self.assertRaises(ValueError):
            timeline.treatments([(1, 1, 1)]*4, 3, 3250)


if __name__ == '__main__':
    unittest.main()
