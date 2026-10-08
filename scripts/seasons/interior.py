#!/usr/bin/env python3
"""Staged interior build with prompt2. usage: interior.py POS FACES LAMPS ASPECT six|four [porch]; env VIEW (extra view sentence)"""
import pilot, prompt2, subprocess, json, sys, os, math
from concurrent.futures import ThreadPoolExecutor
pos, faces, lamps, aspect, n = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3], sys.argv[4], sys.argv[5]; porch = len(sys.argv) > 6
p = f'{pos:02d}'; O = f'{pilot.ROOT}/assets/listing/{p}.webp'; VIEW = os.environ.get('VIEW', '')
W, H = subprocess.run(['magick', 'identify', '-format', '%w %h', O], capture_output=True, text=True).stdout.split()
def run(*a): return subprocess.run(a, capture_output=True, text=True).stdout
def med(f):
    t = run('magick', f, '-colorspace', 'Gray', '-resize', '96x96!', '-depth', '8', 'txt:-').splitlines()[1:]
    v = sorted(int(l.split('gray(')[1].split(')')[0].split('%')[0].split(',')[0]) for l in t if 'gray(' in l); return v[len(v) // 2] / 255
def low(f): return [float(x) for x in run('magick', f, '-gravity', 'South', '-crop', '100%x40%+0+0', '+repage', '-resize', '1x1!', '-format', '%[fx:r] %[fx:g] %[fx:b]', 'info:').split()]
def one(k, base):
    P = prompt2.build_interior(k, faces, lamps=lamps, porch=porch, view_extra=VIEW); out = f'stage/{p}-{k:02d}'
    raw, u = pilot.call([{'text': P}, pilot.img_part(base, pilot.CANVAS[aspect])], aspect); open(out + '-raw.jpg', 'wb').write(raw)
    subprocess.run(['magick', out + '-raw.jpg', '-resize', f'{W}x{H}!', out + '-full.png'], check=True)
    subprocess.run([sys.executable, 'align.py', base, out + '-full.png', out + '-a.png'], capture_output=True)
    r = run(sys.executable, 'align.py', base, out + '-a.png', out + '.png'); j = json.loads(r) if r.strip() else {}
    json.dump({'prompt': P, 'base': base, 'usage': u, 'align': j}, open(out + '.json', 'w'), indent=1)
    print(pos, k, 'shift', j.get('max_shift_px'), 'matched', j.get('inliers'), '/', j.get('patches'), flush=True); return out + '.png'
ONLY = [int(x) for x in os.environ.get('ONLY', '').split()]
with ThreadPoolExecutor(3) as ex: list(ex.map(lambda k: one(k, O), [k for k in (6, 3, 9) if not ONLY or k in ONLY]))
keys = [3, 6, 9]
if n == 'six':
    with ThreadPoolExecutor(2) as ex: list(ex.map(lambda k: one(k, f'stage/{p}-06.png'), [k for k in (5, 8) if not ONLY or k in ONLY]))
    keys = [3, 5, 6, 8, 9]
t = low(f'stage/{p}-03.png'); Y = lambda v: 0.2126 * v[0] + 0.7152 * v[1] + 0.0722 * v[2]; m0 = med(O); log = {}
for k in keys:
    f = f'stage/{p}-{k:02d}.png'; ops = []
    if k in (5, 6, 8):
        c = low(f); g = [max(0.88, min(1.12, (t[i] / Y(t)) / (c[i] / Y(c)))) for i in range(3)]; ops += ['-color-matrix', f'{g[0]} 0 0 0 {g[1]} 0 0 0 {g[2]}']
    m = med(f); gam = max(0.85, min(1.3, math.log(m) / math.log(0.93 * m0))) if m < 0.9 * m0 else 1.0; ops += ['-gamma', f'{gam:.3f}']
    out = f'stage/{p}-{k:02d}-post.png'; subprocess.run(['magick', f, *ops, out], check=True); c = low(out); log[k] = dict(gamma=round(gam, 2), median=round(med(out), 2), RB=round(c[0] / c[2], 2))
    subprocess.run(['magick', O, out, '-evaluate-sequence', 'Mean', '-resize', '380x', f'stage/{p}-{k:02d}-overlay.png'])
json.dump(log, open(f'stage/{p}-post.json', 'w'), indent=1); print(pos, 'original median', round(m0, 2), log, flush=True)
subprocess.run(['magick', f'review/img/{p}/00.webp'] + [f'stage/{p}-{k:02d}-post.png' for k in keys] + ['-resize', '380x', '+append', f'/tmp/claude-501/ia{p}.png'])
subprocess.run(['magick', '-size', '380x10', 'xc:white'] + [f'stage/{p}-{k:02d}-overlay.png' for k in keys] + ['+append', f'/tmp/claude-501/ib{p}.png'])
subprocess.run(['magick', f'/tmp/claude-501/ia{p}.png', f'/tmp/claude-501/ib{p}.png', '-append', f'fin/int{p}.jpg'])
