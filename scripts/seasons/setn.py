#!/usr/bin/env python3
"""Fill a photo's eight in-between whole steps from its four approved anchors with prompt2. usage: setn.py POS LOOKS ASPECT [has_plants]"""
import pilot, prompt2, subprocess, json, sys, os
from concurrent.futures import ThreadPoolExecutor
pos, looks, aspect = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]; plants = len(sys.argv) > 4
R = f'review/img/{pos:02d}'; f = lambda k: f'{R}/{k:02d}.webp'; D = f'set{pos:02d}'; os.makedirs(D, exist_ok=True)
W, H = subprocess.run(['magick', 'identify', '-format', '%w %h', f(0)], capture_output=True, text=True).stdout.split()
PLAN = {
 1:  (0, 3, 'It shows peak fall a month later. Its only job is to show which trees turn color first and where leaves collect. This frame comes long before it and looks much more like IMAGE 1.'),
 2:  (0, 3, 'It shows peak fall two weeks later. Its only job is to show which trees turn color first and where leaves collect. This frame is about halfway to it.'),
 4:  (3, 6, 'It shows midwinter. Its only job is to show the house and the bare branches that appear where leaves have fallen. This frame still has half its leaves and has no snow.'),
 5:  (6, None, None), 7: (6, None, None),
 8:  (6, 9, 'It shows spring. Its only job is to show where the first leaves will open. This frame has only buds and a few tiny leaves.'),
 10: (9, 0, 'It shows full summer. Its only job is to show how full the leaves become. This frame is most of the way there.'),
 11: (0, None, None),
}
for ov in os.environ.get('OVERRIDE', '').split():
    k_, b_ = map(int, ov.split(':')); PLAN[k_] = (b_, None, None)
EXTRA = [e for e in os.environ.get('EXTRA', '').split('|') if e]
def one(k):
    base, sec, job = PLAN[k]; P = prompt2.build(k, looks, has_plants=plants, second=job, has_house=not os.environ.get('NOHOUSE'), extra=EXTRA); out = f'{D}/{k:02d}'
    parts = [{'text': P}, pilot.img_part(f(base), pilot.CANVAS[aspect])] + ([pilot.img_part(f(sec))] if sec is not None else [])
    raw, u = pilot.call(parts, aspect); open(out + '-raw.jpg', 'wb').write(raw)
    subprocess.run(['magick', out + '-raw.jpg', '-resize', f'{W}x{H}!', out + '-full.png'], check=True)
    subprocess.run([sys.executable, 'align.py', f(base), out + '-full.png', out + '-a.png'], capture_output=True)
    r = subprocess.run([sys.executable, 'align.py', f(base), out + '-a.png', out + '.png'], capture_output=True, text=True).stdout
    j = json.loads(r) if r.strip() else {}
    mean = subprocess.run(['magick', out + '.png', '-colorspace', 'Gray', '-format', '%[fx:int(mean*100)]', 'info:'], capture_output=True, text=True).stdout
    json.dump({'step': k, 'base': base, 'second': sec, 'prompt': P, 'usage': u, 'align': j}, open(out + '.json', 'w'), indent=1)
    return k, f"from {base}: shift {j.get('max_shift_px')} matched {j.get('inliers')}/{j.get('patches')} brightness {mean}"
with ThreadPoolExecutor(8) as ex:
    for k, m in ex.map(one, [int(x) for x in os.environ.get('STEPS', '').split()] or list(PLAN)): print(pos, k, m)
for k in (0, 3, 6, 9): subprocess.run(['magick', f(k), f'{D}/{k:02d}.png'])
rows = []
for half in ((0, 1, 2, 3, 4, 5), (6, 7, 8, 9, 10, 11)):
    o = f'/tmp/claude-501/row{pos}{half[0]}.png'; subprocess.run(['magick'] + [f'{D}/{k:02d}.png' for k in half] + ['-resize', '400x', '+append', o]); rows.append(o)
subprocess.run(['magick'] + rows + ['-append', f'fin/set{pos:02d}.jpg'])
