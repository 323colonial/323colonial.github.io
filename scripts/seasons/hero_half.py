#!/usr/bin/env python3
"""Private in-between hero frames at half steps, made with Nano Banana 2.1 from the original photo with the two approved neighbors as references."""
import json, math, os, subprocess, sys
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import pilot
D = pilot.OUT; MASTER = f'{pilot.ROOT}/assets/listing/01.webp'
def run(*a): return subprocess.run(a, capture_output=True, text=True).stdout
def mean(p): return float(run('magick', p, '-colorspace', 'Gray', '-format', '%[fx:mean]', 'info:'))
def one(h):
    lo, hi = int(h), int(h) + 1; name, desc = pilot.S(h)[2], pilot.S(h)[4]; refs = [pilot.hero_ref(lo), pilot.hero_ref(hi)]
    P = (pilot.LOCK + '\n\nSCENE: The front of the house, which faces NORTH, seen from the lawn. The camera looks roughly south-southwest. The house is in wooded mountains at Berkeley Springs, West Virginia (latitude 39.6 N).'
         f'\n\nSEASON AND TIME: Frame {h} on a 12-step year, "{name}". {desc} {pilot.sun_text(h)}'
         f' IMAGE 2 is the approved frame of this same photograph at step {lo}, just BEFORE this one. IMAGE 3 is the approved frame at step {hi}, just AFTER it. '
         'Produce the natural state halfway between them: the same trees, with leaf cover halfway between; the same patches of frost and snow, halfway in extent, in the same places; ground color halfway; and light, sky color and overall darkness halfway between the two. '
         'It must read as one continuous change when the three frames are dissolved in order. Take structure and exact geometry from IMAGE 1, and appearance from IMAGE 2 and IMAGE 3. '
         + pilot.WINDOWS[int(h)] + ' The window glow matches IMAGE 2 and IMAGE 3. Keep the cedar siding, stone and roof the same hue as in those frames.'
         '\n\nCHANGE ONLY: foliage, ground cover, frost and snow, sky, and the light, as described.')
    s = f'{D}/hero/{pilot.lab(h)}'
    os.makedirs(os.path.dirname(s), exist_ok=True)
    raw, usage = pilot.call([{'text': P}, pilot.img_part(MASTER, '2528x1696')] + [pilot.img_part(r) for r in refs], '3:2')
    open(s + '-raw.jpg', 'wb').write(raw); run('magick', s + '-raw.jpg', '-resize', '1280x848!', s + '-full.png')
    run(sys.executable, f'{pilot.HERE}/align.py', MASTER, s + '-full.png', s + '-a.png'); al = run(sys.executable, f'{pilot.HERE}/align.py', MASTER, s + '-a.png', s + '.png').strip(); os.remove(s + '-a.png')
    target = (mean(refs[0]) + mean(refs[1])) / 2; got = mean(s + '.png'); g = max(0.7, min(1.4, math.log(got) / math.log(target)))
    run('magick', s + '.png', '-gamma', f'{g:.3f}', s + '.png')
    j = json.loads(al) if al else {}
    json.dump({'step': h, 'model': pilot.MODEL, 'prompt': P, 'refs': [os.path.relpath(r, D) for r in refs], 'usage': usage, 'align': j, 'gamma': g}, open(s + '.json', 'w'), indent=1)
    return h, f"shift {j.get('max_shift_px')} inliers {j.get('inliers')}/{j.get('patches')} brightness {got:.2f} -> target {target:.2f} (gamma {g:.2f})"
if __name__ == '__main__':
    with ThreadPoolExecutor(6) as ex:
        for h, msg in ex.map(one, [float(a) for a in sys.argv[1:]]): print(h, msg)
