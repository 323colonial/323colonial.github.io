#!/usr/bin/env python3
"""In-between frame made by resolving the 50% dissolve of its two approved neighbors into one sharp photograph.
The dissolve already has the right layout, snow extent, color and brightness, so the model only has to remove the double exposure.
usage: tween.py TAG ID:STEP ...   (ID is a review/img folder, e.g. 01, 39, 41)"""
import json, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pilot, smooth
D = pilot.OUT
def run(*a): return subprocess.run(a, capture_output=True, text=True).stdout
def one(job):
    tag, pid, h = job; lo, hi = int(h), int(h) + 1
    A, B = f'{D}/review/img/{pid}/{lo:02d}.webp', f'{D}/review/img/{pid}/{hi:02d}.webp'
    d = f'{D}/{tag}/{pid}'; os.makedirs(d, exist_ok=True); s = f'{d}/{pilot.lab(h)}'; blend = s + '-blend.png'
    run('magick', A, B, '-evaluate-sequence', 'Mean', blend)
    w, hh = run('magick', 'identify', '-format', '%w %h', blend).split(); aspect = '4:3' if int(w) / int(hh) < 1.4 else '3:2'
    name, desc = (pilot.S(h)[2], pilot.S(h)[4]) if h in pilot.HALF else ('the moment between the two', 'Everything is halfway between IMAGE 2 and IMAGE 3.')
    P = ('IMAGE 1 is an exact 50% double exposure of two approved photographs of the same scene from a locked camera: IMAGE 2, taken just before, and IMAGE 3, taken just after. '
         'Turn IMAGE 1 into ONE clean, sharp, single-exposure photograph of the moment halfway between them. This is a clean-up of IMAGE 1, not a new picture. '
         'Keep IMAGE 1 exactly as it is in composition, geometry, overall brightness, color balance, sky gradient and cloud positions, and in where snow, frost, bare ground, grass and leaves lie. Every building edge, window, trunk and branch stays at its coordinate. '
         'Change only what is needed to remove the ghosting: where IMAGE 1 shows two faint overlaid versions of something, such as leaves over bare branches, half-transparent snow, or doubled shadows, replace them with one solid, physically plausible in-between state '
         '(fewer leaves, thinner or smaller patches of snow at the same places, one set of soft shadows). Where IMAGE 2 and IMAGE 3 agree, leave IMAGE 1 untouched. Do not add anything that appears in neither. '
         f'For orientation only, the moment is "{name}": {desc} '
         'Do not brighten, darken, re-color or re-light the picture. Keep the watermark in the lower-left corner. Return ONE full-frame photograph.')
    raw, usage = pilot.call([{'text': P}, pilot.img_part(blend, pilot.CANVAS[aspect]), pilot.img_part(A), pilot.img_part(B)], aspect)
    open(s + '-raw.jpg', 'wb').write(raw); run('magick', s + '-raw.jpg', '-resize', f'{w}x{hh}!', s + '-full.png')
    _, al = pilot.align_twice(blend, s)
    tmpdir = s + '-tmp'; os.makedirs(tmpdir, exist_ok=True)
    j = json.loads(al) if al else {}; det, off, ab = smooth.score(A, s + '.png', B, tmp=tmpdir)
    json.dump({'id': pid, 'step': h, 'model': pilot.MODEL, 'prompt': P, 'usage': usage, 'align': j, 'detour': det, 'off': off}, open(s + '.json', 'w'), indent=1)
    return f"{pid} {h}: detour {det} (off {off}) shift {j.get('max_shift_px')} inliers {j.get('inliers')}/{j.get('patches')}"
if __name__ == '__main__':
    tag = sys.argv[1]; jobs = [(tag, a.split(':')[0], float(a.split(':')[1])) for a in sys.argv[2:]]
    with ThreadPoolExecutor(10) as ex:
        for m in ex.map(one, jobs): print(m)
