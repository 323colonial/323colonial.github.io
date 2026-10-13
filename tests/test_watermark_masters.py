"""Private lossless evidence check; run with existing LaMa venv, not dependency-free CI."""
import hashlib
import json
from pathlib import Path
import unittest

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '.pi/artifacts/colonial-6nu'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class WatermarkMasters(unittest.TestCase):
    def test_every_saved_master_mask_and_delivery(self):
        report = json.loads((WORK / 'conversion.json').read_text())
        self.assertEqual(len(report['previews']), 2)
        self.assertEqual({p['path'] for p in report['previews']}, {
            'assets/email/323-colonial-hero.gif', 'assets/email/323-colonial-hero-small.gif'})
        self.assertEqual(len(report['images']), 470)
        self.assertEqual(sum(r['mask_xyxy'] is not None for r in report['images']), 426)
        for r in report['images']:
            with self.subTest(path=r['path']):
                source = WORK / 'originals' / r['path']
                self.assertEqual(digest(source), r['source_sha256'])
                self.assertEqual(digest(WORK / 'originals' / r['small']['path']), r['small']['source_sha256'])
                original = Image.open(source).convert('RGB')
                self.assertEqual(list(original.size), r['size'])
                if r['mask_xyxy'] is None:
                    self.assertEqual(digest(ROOT / r['path']), r['source_sha256'])
                    self.assertEqual(digest(ROOT / r['small']['path']), r['small']['source_sha256'])
                    continue
                master = WORK / 'masters' / Path(r['path']).with_suffix('.png')
                mask = WORK / 'masks' / Path(r['path']).with_suffix('.png')
                self.assertEqual(digest(master), r['master_sha256'])
                self.assertEqual(digest(mask), r['mask_sha256'])
                result = Image.open(master).convert('RGB')
                with Image.open(mask) as saved_mask:
                    mask_image = saved_mask.copy()
                self.assertEqual(result.size, original.size)
                self.assertEqual(mask_image.size, original.size)
                self.assertEqual(mask_image.mode, 'L')
                expected = np.zeros((original.height, original.width), dtype=np.uint8)
                x0, y0, x1, y1 = r['mask_xyxy']
                expected[y0:y1, x0:x1] = 255
                np.testing.assert_array_equal(np.asarray(mask_image), expected)
                a, b, selected = np.asarray(original), np.asarray(result), expected > 0
                np.testing.assert_array_equal(a[~selected], b[~selected])
                self.assertTrue(np.any(a[selected] != b[selected]))
                for record in (r, r['small']):
                    delivery = WORK / 'stage' / record['path']
                    self.assertEqual(digest(delivery), record['output_sha256'])
                    with Image.open(delivery) as delivered_image:
                        self.assertEqual(list(delivered_image.size), record['size'])
                decoded = np.asarray(Image.open(WORK / 'stage' / r['path']).convert('RGB'))
                delta = np.abs(decoded.astype('int16') - b.astype('int16'))[~selected]
                self.assertEqual(float(delta.mean()), r['delivery_outside_mask_mean_absolute_error'])
                self.assertEqual(int(delta.max()), r['delivery_outside_mask_max_absolute_error'])
        for r in report['previews']:
            self.assertEqual(digest(WORK / 'originals' / r['path']), r['source_sha256'])
            self.assertEqual(digest(WORK / 'stage' / r['path']), r['output_sha256'])
            im = Image.open(WORK / 'stage' / r['path'])
            self.assertEqual(list(im.size), r['size'])
            self.assertEqual(im.n_frames, 120)
            self.assertEqual(im.info['loop'], 0)
            for i in range(im.n_frames):
                im.seek(i)
                self.assertEqual(im.info['duration'], 200)
            im.close()


if __name__ == '__main__':
    unittest.main()
