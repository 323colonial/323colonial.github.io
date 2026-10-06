"""Check independent architectural landmarks with local edge correlation (ImageMagick)."""
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile

root = Path(__file__).resolve().parent
version = sys.argv[1] if len(sys.argv) > 1 else 'v2'
assert version in ('v2', 'v3'), 'Usage: measure-alignment.py [v2|v3]'
work = Path('.pi/artifacts/seasons') / version
sources = {name: (work / ('spring-lush.png' if name == 'spring' else f'{name}-unregistered.png'), root / f'v2/{name}.webp') for name in ('spring', 'fall', 'winter')}
if version == 'v3':
    sources = {record['sequence_id']: (work / f"{record['id']}-unregistered.png", Path(record['preview_path'])) for record in json.loads((root / 'v3/provenance.json').read_text())['images']}
# Validation points are not the wall-texture fitting regions in align.swift.
points = {'main_dormer_peak': (614, 124), 'dormer_window_foot': (581, 291),
          'porch_post_top': (814, 383), 'porch_post_foot': (961, 548),
          'garage_jamb_top': (1035, 444), 'deck_newel': (422, 541),
          'bird_feeder_pole': (697, 575), 'birdbath': (1087, 638)}
# These four retain comparable structure even under snow and glowing glass.
# ponytail: NCC cannot certify changed/occluded surfaces; review porch/snow crops visually.
verified_points = ('main_dormer_peak', 'dormer_window_foot', 'garage_jamb_top', 'deck_newel')
report = {}
with tempfile.TemporaryDirectory() as folder:
    folder = Path(folder)
    master = folder / 'master.png'
    subprocess.run(['magick', str(root / 'v2/summer.jpg'), '-colorspace', 'gray', '-morphology', 'Edge', 'Diamond:1', str(master)], check=True)
    for season, pair in sources.items():
        report[season] = {}
        for version, source in zip(('before', 'after'), pair):
            edges = folder / 'edges.png'
            subprocess.run(['magick', str(source), '-colorspace', 'gray', '-morphology', 'Edge', 'Diamond:1', str(edges)], check=True)
            values = {}
            for name, (x, y) in points.items():
                patch, search = folder / 'patch.png', folder / 'search.png'
                subprocess.run(['magick', str(master), '-crop', f'64x64+{x-32}+{y-32}', '+repage', str(patch)], check=True)
                subprocess.run(['magick', str(edges), '-crop', f'96x96+{x-48}+{y-48}', '+repage', str(search)], check=True)
                result = subprocess.run(['magick', 'compare', '-metric', 'NCC', '-subimage-search', str(search), str(patch), 'null:'], capture_output=True, text=True)
                match = re.search(r'@ (\d+),(\d+) \[([\d.eE+-]+)\]', result.stderr)
                assert result.returncode in (0, 1) and match, result.stderr
                dx, dy = int(match[1]) - 16, int(match[2]) - 16
                values[name] = {'dx_px': dx, 'dy_px': dy, 'distance_px': round(math.hypot(dx, dy), 3), 'correlation': float(match[3])}
            report[season][version] = values
        before = [report[season]['before'][name]['distance_px'] for name in verified_points]
        after = [report[season]['after'][name]['distance_px'] for name in verified_points]
        print(f'{season}: mean landmark displacement {sum(before)/len(before):.2f}px → {sum(after)/len(after):.2f}px; maximum {max(after):.2f}px')
(work / 'landmark-check.json').write_text(json.dumps(report, indent=2) + '\n')
for season, versions in report.items():
    architectural = [versions['after'][name] for name in verified_points]
    assert all(v['correlation'] > .4 and v['distance_px'] <= 2 for v in architectural), f'{season}: comparable architectural landmark exceeds 2px or cannot be matched confidently; inspect report'
print('PASS: four comparable architectural landmarks within 2px in each season. Changed snow/porch/pole regions still require visual review.')
