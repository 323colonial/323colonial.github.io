"""Rebuild four day-cycle frames from tracked v4 assets; run from any directory.
Requires existing ImageMagick only. No generation, resampling or coordinate warp.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[1]
output = root / 'v5'
master = root / 'v2/summer.jpg'
settings = {
    'first-frost': ('Deep dusk', (.58, .60, .76), .30),
    'first-snow': ('Late evening', (.38, .44, .60), .66),
    'winter': ('Blue dawn', (.88, .92, 1.02), .12),
    'snowmelt': ('Sunrise', (1.08, 1.04, .97), 0),
}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def magick(*args):
    subprocess.run(['magick', *map(str, args)], check=True)

def value(path, expression):
    return subprocess.check_output(['magick', str(path), '-format', expression, 'info:'], text=True)

assert sha(master) == '6d91f6f3993b5014b1be640c8a2eb51428762af3f05c35beed9bec26147bd9ab'
sources = [master, root / 'v2/winter.webp', root / 'v2/provenance.json', *sorted((root / 'v4').glob('*'))]
source_hashes = {str(p.relative_to(root)): sha(p) for p in sources if p.is_file()}
polygons = json.loads((root / 'v2/provenance.json').read_text())['fall_window_treatment']['polygons_master_pixels']
records = []
with tempfile.TemporaryDirectory() as folder:
    work = Path(folder)
    glass, fixtures, mask = (work / name for name in ('glass.png', 'fixtures.png', 'mask.png'))
    draw = ' '.join('polygon ' + ' '.join(f'{x},{y}' for x, y in polygon) for polygon in polygons)
    magick('-size', '1280x848', 'xc:black', '-fill', 'white', '-draw', draw, '-blur', '0x1', glass)
    magick('-size', '1280x848', 'xc:black', '-fill', 'white', '-draw',
           'ellipse 395,395 23,29 0,360 ellipse 774,418 20,26 0,360 ellipse 849,424 17,24 0,360 ellipse 1147,465 13,20 0,360',
           '-blur', '0x7', fixtures)
    magick(glass, fixtures, '-evaluate-sequence', 'max', mask)
    watermark = work / 'watermark.png'
    magick(master, '-crop', '137x45+0+803', '+repage', watermark)
    for slug, (day, rgb, warmth) in settings.items():
        source = root / f'v4/{slug}.webp'
        graded, lit, alpha, overlay = (work / name for name in ('graded.png', 'lit.png', 'alpha.png', 'overlay.png'))
        r, g, b = rgb
        magick(source, '-color-matrix', f'{r} 0 0 0 {g} 0 0 0 {b}', graded)
        magick(mask, '-evaluate', 'multiply', warmth, alpha)
        magick(root / 'v2/winter.webp', alpha, '-alpha', 'off', '-compose', 'CopyOpacity', '-composite', overlay)
        magick(graded, overlay, '-compose', 'Over', '-composite', lit)
        # Local practical lights must not brighten sky, snowbank or grill.
        for x, y in ((500, 50), (300, 750), (360, 458)):
            pixel = f'%[pixel:p{{{x},{y}}}]'
            assert value(graded, pixel) == value(lit, pixel), 'Practical-light mask leaked'
        destination = output / f'{slug}.webp'
        magick(lit, watermark, '-geometry', '+0+803', '-composite', '-strip', '-quality', '90', destination)
        assert value(destination, '%wx%h') == '1280x848'
        sky = float(subprocess.check_output(['magick', str(destination), '-crop', '1x1+500+50', '+repage', '-colorspace', 'gray', '-format', '%[fx:mean]', 'info:'], text=True))
        records.append({'id': slug, 'day_stage': day, 'source': str(source.relative_to(root)),
                        'source_sha256': sha(source), 'rgb_multipliers': rgb,
                        'additional_warm_source_mix': warmth, 'preview_path': f'v5/{slug}.webp',
                        'preview_sha256': sha(destination), 'sky_sample': sky})
    sky = {record['id']: record['sky_sample'] for record in records}
    assert sky['first-snow'] < sky['first-frost'] < sky['winter'] < sky['snowmelt'], sky
assert all(sha(root / name) == digest for name, digest in source_hashes.items()), 'An original source changed'
manifest = {
    'method': 'Tone-only day-cycle relighting of four registered v4 frames. No new generation or coordinate transform; original snowbank contours and grass texture retained.',
    'cycle_ms': 10000, 'images': records, 'source_hashes': source_hashes,
    'warm_source': 'v2/winter.webp', 'glass_geometry_source': 'v2/provenance.json fall_window_treatment.polygons_master_pixels',
    'recipe': 'v5/relight.py', 'recipe_sha256': sha(Path(__file__)),
    'checks': ['Immutable source hashes', '1280x848 outputs', 'Night darkest, then dusk, dawn, sunrise sky sample', 'Practical-light mask leaves sky, snowbank and grill samples untouched'],
    'limits': 'Art-directed exposure/color simulation, not physically traced lighting. Inherits unresolved v4 landmark-check failures; no alignment pass claimed. Owner review pending; colonial-29s stays open.'
}
(output / 'provenance.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('PASS: four day-cycle frames; source hashes, masked-light isolation, dimensions and sky ordering checked.')
