"""Check final lighting edits against their v5 inputs, not against another season.
Uses the same local edge NCC method as ../measure-alignment.py; no raw files needed.
"""
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import tempfile

root = Path(__file__).resolve().parent.parent
manifest = json.loads((root / 'v6/provenance.json').read_text())
points = {'main_dormer_peak': (614,124), 'dormer_window_foot': (581,291),
          'porch_post_top': (814,383), 'porch_post_foot': (961,548),
          'garage_jamb_top': (1035,444), 'deck_newel': (422,541),
          'bird_feeder_pole': (697,575), 'birdbath': (1087,638),
          'grill': (364,463), 'chimney': (301,209),
          'snow_edge': (775,734), 'foreground_leaves': (536,761)}
assert hashlib.sha256((root / 'v2/summer.jpg').read_bytes()).hexdigest() == manifest['summer_sha256']
with tempfile.TemporaryDirectory() as folder:
    folder = Path(folder)
    for record in manifest['images']:
        slug = record['id']
        for version, key in [('v5', 'source_sha256'), ('v6', 'preview_sha256')]:
            image = root / version / f'{slug}.webp'
            assert hashlib.sha256(image.read_bytes()).hexdigest() == record[key], f'{slug}: {version} hash changed'
            size = subprocess.check_output(['magick', 'identify', '-format', '%wx%h', str(image)], text=True)
            assert size == '1280x848', f'{slug}: {version} dimensions changed'
            subprocess.run(['magick', str(image), '-colorspace', 'gray', '-morphology', 'Edge', 'Diamond:1', str(folder / f'{version}.png')], check=True)
        values = []
        for name, (x, y) in points.items():
            patch, search = folder / 'patch.png', folder / 'search.png'
            subprocess.run(['magick', str(folder / 'v5.png'), '-crop', f'64x64+{x-32}+{y-32}', '+repage', str(patch)], check=True)
            subprocess.run(['magick', str(folder / 'v6.png'), '-crop', f'96x96+{x-48}+{y-48}', '+repage', str(search)], check=True)
            result = subprocess.run(['magick', 'compare', '-metric', 'NCC', '-subimage-search', str(search), str(patch), 'null:'], capture_output=True, text=True)
            match = re.search(r'@ (\d+),(\d+) \[([\d.eE+-]+)\]', result.stderr)
            assert result.returncode in (0, 1) and match, result.stderr
            distance, correlation = math.hypot(int(match[1])-16, int(match[2])-16), float(match[3])
            assert distance <= 2 and correlation > .4, f'{slug}/{name}: {distance:.3f}px, NCC{correlation:.3f}'
            values.append((distance, correlation))
        print(f'PASS {slug}: 12 input-relative landmarks, max{max(v[0] for v in values):.3f}px, minNCC{min(v[1] for v in values):.3f}; hashes/dimensions match')
print('Sampled alignment only; not pixel identity or full-sequence alignment clearance.')
