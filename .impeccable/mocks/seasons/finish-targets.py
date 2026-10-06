"""Finish private seasonal targets from registered intermediates; preserve summer bytes."""
import hashlib
import json
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parent
assets = root / 'v2'
work = Path('.pi/artifacts/seasons/v2')
master = assets / 'summer.jpg'
assert hashlib.sha256(master.read_bytes()).hexdigest() == '6d91f6f3993b5014b1be640c8a2eb51428762af3f05c35beed9bec26147bd9ab'

def magick(*args):
    subprocess.run(['magick', *map(str, args)], check=True)

# Glass only; coordinate polygons stay anchored to unchanged master.
windows = [
    [(357, 193), (390, 318), (390, 350), (358, 366)],
    [(359, 399), (373, 393), (373, 454), (359, 454)],
    [(589, 211), (631, 223), (631, 283), (589, 275)],
    [(580, 390), (625, 394), (625, 477), (580, 476)],
    [(636, 396), (686, 400), (686, 480), (636, 479)],
    [(795, 429), (803, 426), (807, 443), (805, 471), (797, 474)],
    [(926, 428), (946, 432), (946, 481), (926, 481)],
    [(965, 433), (974, 434), (974, 474), (965, 474)],
    [(1054, 331), (1068, 335), (1068, 380), (1054, 377)],
    [(1039, 455), (1057, 458), (1057, 470), (1039, 467)],
    [(1090, 460), (1115, 463), (1115, 475), (1090, 472)]
]
draw = ' '.join('polygon ' + ' '.join(f'{x},{y}' for x, y in polygon) for polygon in windows)
mask = work / 'fall-glass-mask.png'
magick('-size', '1280x848', 'xc:black', '-fill', 'white', '-draw', draw,
       '-blur', '0x1', '-evaluate', 'multiply', '.75', mask)
reflection = work / 'fall-subtle-reflection.png'
magick(master, '-modulate', '85,70,100', '-fill', '#bc824a', '-colorize', '12%', reflection)
overlay = work / 'fall-glass-overlay.png'
magick(reflection, mask, '-alpha', 'off', '-compose', 'CopyOpacity', '-composite', overlay)
fall = work / 'fall-subtle.png'
magick(work / 'fall-affine.png', overlay, '-compose', 'Over', '-composite', fall)
# Regression: a glass mask must not relight the rest of the scene.
def sky_pixel(path):
    return subprocess.check_output(['magick', str(path), '-format', '%[pixel:p{500,50}]', 'info:'], text=True)
assert sky_pixel(fall) == sky_pixel(work / 'fall-affine.png'), 'Window-only dimming changed the sky'
watermark = work / 'master-watermark.png'
magick(master, '-crop', '137x45+0+803', '+repage', watermark)
manifest = json.loads((assets / 'provenance.json').read_text())
for season, input_name in [('spring', 'spring-lush-affine.png'), ('fall', 'fall-subtle.png'), ('winter', 'winter-affine.png')]:
    output = assets / f'{season}.webp'
    magick(work / input_name, watermark, '-geometry', '+0+803', '-composite', '-strip', '-quality', '90', output)
    record = manifest['images'][season]
    record['preview_path'] = str(output.relative_to(Path.cwd()))
    record['preview_sha256'] = hashlib.sha256(output.read_bytes()).hexdigest()
    stats_name = 'spring-lush-affine.png.json' if season == 'spring' else f'{season}-affine.png.json'
    record['registration'] = json.loads((work / stats_name).read_text())
manifest['fall_window_treatment'] = {'polygons_master_pixels': windows, 'original_reflection_mix': .75, 'reflection_brightness_percent': 85, 'reflection_saturation_percent': 70, 'warm_tint': '#bc824a at 12%', 'mask_feather_sigma': 1}
manifest['finishing'] = 'finish-targets.py restores unchanged master watermark crop at x0/y803, 137x45; WebP quality90. Summer JPEG byte-identical. Global robust affine camera registration only, no dense seasonal warp.'
manifest['status'] = 'Private revised AI seasonal concepts. Architectural camera alignment corrected; generated textures are not identical to original. Four targets for owner review, no 24-frame sequence or public integration.'
(assets / 'provenance.json').write_text(json.dumps(manifest, indent=2) + '\n')
print('Finished three registered targets; original late summer unchanged')
