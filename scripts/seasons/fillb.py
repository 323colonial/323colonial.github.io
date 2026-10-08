#!/usr/bin/env python3
"""Fill a batch photo from its approved set of four to 12 steps, using its batch.CFG. usage: fillb.py POS"""
import pilot, prompt2, batch, subprocess, json, sys, os
from concurrent.futures import ThreadPoolExecutor
pos = int(sys.argv[1]); pid = f'{pos:02d}'; c0 = dict(batch.CFG[pos]); aspect = c0.pop('aspect')
R = f'review/img/{pid}'; D = f'fill{pid}'; os.makedirs(D, exist_ok=True); f = lambda k: f'{R}/{k:02d}.webp'
W, H = subprocess.run(['magick', 'identify', '-format', '%w %h', f(0)], capture_output=True, text=True).stdout.split()
SEC = {1: (3, 'It shows peak fall a month later. Its only job is to show which trees turn color first and where leaves collect. This frame comes long before it and looks much more like IMAGE 1.'),
       2: (3, 'It shows peak fall two weeks later. Its only job is to show which trees turn color first and where leaves collect. This frame is about halfway to it.'),
       4: (6, 'It shows midwinter. Its only job is to show the bare branches that appear where leaves have fallen. This frame still has half its leaves and has no snow.')}
def make(k, base, prev=False):
    c = dict(c0); c['extra'] = [e.format(garden='the plants are there, as in IMAGE 1' if k in (0, 1, 10, 11) else 'the plants are gone and the beds are bare soil') for e in c.get('extra', [])]
    sec = SEC.get(k); P = prompt2.build(k, second=sec[1] if sec else None, prev=prev, **c); out = f'{D}/{k:02d}'
    raw, u = pilot.call([{'text': P}, pilot.img_part(base, pilot.CANVAS[aspect])] + ([pilot.img_part(f(sec[0]))] if sec else []), aspect); open(out + '-raw.jpg', 'wb').write(raw)
    subprocess.run(['magick', out + '-raw.jpg', '-resize', f'{W}x{H}!', out + '-full.png'], check=True)
    subprocess.run([sys.executable, 'align.py', base, out + '-full.png', out + '-a.png'], capture_output=True)
    r = subprocess.run([sys.executable, 'align.py', base, out + '-a.png', out + '.png'], capture_output=True, text=True).stdout; j = json.loads(r) if r.strip() else {}
    json.dump({'step': k, 'base': base, 'prompt': P, 'usage': u, 'align': j}, open(out + '.json', 'w'), indent=1)
    print(pid, k, 'shift', j.get('max_shift_px'), 'matched', j.get('inliers'), '/', j.get('patches'), flush=True); return out + '.png'
def chain(): make(8, make(7, f(6), prev=True), prev=True)
with ThreadPoolExecutor(7) as ex:
    fs = [ex.submit(make, 1, f(0)), ex.submit(make, 2, f(0)), ex.submit(make, 11, f(0)), ex.submit(make, 10, f(0)), ex.submit(make, 4, f(3)), ex.submit(make, 5, f(6)), ex.submit(chain)]
    for x in fs: x.result()
rows = []
for half in ((0, 1, 2, 3, 4, 5), (6, 7, 8, 9, 10, 11)):
    o = f'/tmp/claude-501/fb{pid}{half[0]}.png'; subprocess.run(['magick'] + [(f'{D}/{k:02d}.png' if os.path.exists(f'{D}/{k:02d}.png') else f(k)) for k in half] + ['-resize', '400x266!', '+append', o]); rows.append(o)
subprocess.run(['magick'] + rows + ['-append', f'fin/fill{pid}.jpg'])
