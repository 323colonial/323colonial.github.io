"""Offline static photo authoring; approval fixtures remain independent."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/build-listing.py'


class Authoring(unittest.TestCase):
    def load(self):
        self.assertTrue(SCRIPT.is_file(), 'offline figure generator missing')
        spec = importlib.util.spec_from_file_location('build_listing', SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_static_parity_and_idempotence(self):
        build = self.load()
        photos = json.loads((ROOT / 'assets/listing/manifest.json').read_text())['photos']
        for name in ('index.html', 'gallery.html'):
            original = (ROOT / name).read_text()
            generated = build.render_page(original, name, photos)
            self.assertEqual(generated, original)
            self.assertEqual(build.render_page(generated, name, photos), generated)
        result = subprocess.run([sys.executable, str(SCRIPT), '--check'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_metadata_propagates_and_escapes_without_provenance(self):
        build = self.load()
        photos = json.loads((ROOT / 'assets/listing/manifest.json').read_text())['photos']
        photos[1]['caption'] = 'A & B <view> "quoted"'
        photos[1]['source'] = 'PRIVATE_SENTINEL'
        for name, count in [('index.html', 2), ('gallery.html', 1)]:
            rendered = build.render_page((ROOT / name).read_text(), name, photos)
            self.assertEqual(rendered.count('A &amp; B &lt;view&gt; &quot;quoted&quot;'), count * 3)
            self.assertNotIn('PRIVATE_SENTINEL', rendered)

    def test_invalid_metadata_or_markers_fail_closed(self):
        build = self.load()
        photos = json.loads((ROOT / 'assets/listing/manifest.json').read_text())['photos']
        original = (ROOT / 'gallery.html').read_text()
        for field, value in [('path', '../private.webp'), ('width', 0), ('height', '480')]:
            bad = copy.deepcopy(photos)
            bad[0]['derivatives'][0][field] = value
            with self.assertRaises(ValueError):
                build.render_page(original, 'gallery.html', bad)
        with self.assertRaises(ValueError):
            build.render_page(original, 'gallery.html', photos + [photos[0]])
        with self.assertRaises(ValueError):
            build.render_page(original.replace('<!-- photos:gallery -->', ''), 'gallery.html', photos)

    def test_overlapping_and_reversed_regions_rejected(self):
        build = self.load()
        photos = json.loads((ROOT / 'assets/listing/manifest.json').read_text())['photos']
        original = (ROOT / 'index.html').read_text()
        overlap = original.replace('<!-- photos:catalog -->', '').replace(
            '<!-- photos:hero -->', '<!-- photos:catalog --><!-- photos:hero -->')
        reversed_ = original.replace('<!-- photos:hero -->', '<!-- temporary -->').replace(
            '<!-- /photos:hero -->', '<!-- photos:hero -->').replace('<!-- temporary -->', '<!-- /photos:hero -->')
        for invalid in (overlap, reversed_):
            with self.assertRaises(ValueError):
                build.render_page(invalid, 'index.html', photos)

    def test_check_detects_drift_without_writes(self):
        self.load()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'assets/listing').mkdir(parents=True)
            (root / 'assets/listing/manifest.json').write_bytes((ROOT / 'assets/listing/manifest.json').read_bytes())
            for name in ('index.html', 'gallery.html'):
                (root / name).write_bytes((ROOT / name).read_bytes())
            page = root / 'gallery.html'
            page.write_text(page.read_text().replace('Distinctive, locally built', 'Drift, locally built'))
            before = page.read_bytes()
            result = subprocess.run([sys.executable, str(SCRIPT), '--root', tmp, '--check'], capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(page.read_bytes(), before)
            subprocess.run([sys.executable, str(SCRIPT), '--root', tmp], check=True, capture_output=True)
            self.assertEqual(page.read_bytes(), (ROOT / 'gallery.html').read_bytes())


if __name__ == '__main__':
    unittest.main()
