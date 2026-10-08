#!/usr/bin/env python3
"""Fill a review tile from its approved set of four to 12 whole steps with prompt2 (thaw chained), then half steps by dissolve cleanup.
usage: fill.py ID LOOKS ASPECT   e.g. fill.py 01r 200 3:2"""
import pilot, prompt2, subprocess, json, sys, os
from concurrent.futures import ThreadPoolExecutor
pid, looks, aspect = sys.argv[1], int(sys.argv[2]), sys.argv[3]
R = f'review/img/{pid}'; D = f'fill{pid}'; os.makedirs(D, exist_ok=True); f = lambda k: f'{R}/{k:02d}.webp'
W, H = subprocess.run(['magick', 'identify', '-format', '%w %h', f(0)], capture_output=True, text=True).stdout.split()
SEC = {1: (3, 'It shows peak fall a month later. Its only job is to show which trees turn color first and where leaves collect. This frame comes long before it and looks much more like IMAGE 1.'),
       2: (3, 'It shows peak fall two weeks later. Its only job is to show which trees turn color first and where leaves collect. This frame is about halfway to it.'),
       4: (6, 'It shows midwinter. Its only job is to show the bare branches that appear where leaves have fallen. This frame still has half its leaves and has no snow.')}
def make(k, base, prev=False):
    sec = SEC.get(k); P = prompt2.build(k, looks, has_plants=True, second=sec[1] if sec else None, prev=prev); out = f'{D}/{k:02d}'
    parts = [{'text': P}, pilot.img_part(base, pilot.CANVAS[aspect])] + ([pilot.img_part(f(sec[0]))] if sec else [])
    raw, u = pilot.call(parts, aspect); open(out + '-raw.jpg', 'wb').write(raw)
    subprocess.run(['magick', out + '-raw.jpg', '-resize', f'{W}x{H}!', out + '-full.png'], check=True)
    subprocess.run([sys.executable, 'align.py', base, out + '-full.png', out + '-a.png'], capture_output=True)
    r = subprocess.run([sys.executable, 'align.py', base, out + '-a.png', out + '.png'], capture_output=True, text=True).stdout; j = json.loads(r) if r.strip() else {}
    json.dump({'step': k, 'base': base, 'prompt': P, 'usage': u, 'align': j}, open(out + '.json', 'w'), indent=1)
    subprocess.run(['magick', out + '.png', '-quality', '84', f(k)])
    print(pid, k, 'shift', j.get('max_shift_px'), 'matched', j.get('inliers'), '/', j.get('patches'), flush=True); return f(k)
def chain(): make(8, make(7, f(6), prev=True), prev=True)
with ThreadPoolExecutor(8) as ex:
    fs = [ex.submit(make, 1, f(0)), ex.submit(make, 2, f(0)), ex.submit(make, 11, f(0)), ex.submit(make, 10, f(0)), ex.submit(make, 4, f(3)), ex.submit(make, 5, f(6)), ex.submit(chain)]
    for x in fs: x.result()
