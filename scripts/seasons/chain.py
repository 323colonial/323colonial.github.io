#!/usr/bin/env python3
"""Richer thaw and late-spring frames: 7 from 6, 8 from the new 7, 10 from 9. usage: chain.py POS LOOKS ASPECT [plants]; env NOHOUSE, EXTRA"""
import pilot, prompt2, subprocess, json, sys, os
from concurrent.futures import ThreadPoolExecutor
pos, looks, aspect = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]; plants = len(sys.argv) > 4
p = f'{pos:02d}'; D = f'rich{p}'; os.makedirs(D, exist_ok=True); R = f'review/img/{p}'; O = f'review/orig/{p}.webp'
EXTRA = [e for e in os.environ.get('EXTRA', '').split('|') if e]
W, H = subprocess.run(['magick', 'identify', '-format', '%w %h', f'{R}/06.webp'], capture_output=True, text=True).stdout.split()
def make(k, base):
    P = prompt2.build(k, looks, has_house=not os.environ.get('NOHOUSE'), has_plants=plants, prev=True, extra=EXTRA); out = f'{D}/{k:02d}'
    raw, u = pilot.call([{'text': P}, pilot.img_part(base, pilot.CANVAS[aspect])], aspect); open(out + '-raw.jpg', 'wb').write(raw)
    subprocess.run(['magick', out + '-raw.jpg', '-resize', f'{W}x{H}!', out + '-full.png'], check=True)
    subprocess.run([sys.executable, 'align.py', base, out + '-full.png', out + '-a.png'], capture_output=True)
    r = subprocess.run([sys.executable, 'align.py', base, out + '-a.png', out + '.png'], capture_output=True, text=True).stdout
    j = json.loads(r) if r.strip() else {}; json.dump({'step': k, 'base': base, 'prompt': P, 'usage': u, 'align': j}, open(out + '.json', 'w'), indent=1)
    subprocess.run(['magick', O, out + '.png', '-evaluate-sequence', 'Mean', '-resize', '420x', out + '-overlay.png'])
    print(pos, k, 'shift', j.get('max_shift_px'), 'matched', j.get('inliers'), '/', j.get('patches'), 'applied', j.get('applied'), flush=True); return out + '.png'
with ThreadPoolExecutor(2) as ex:
    f10 = ex.submit(make, 10, f'{R}/09.webp'); s7 = make(7, f'{R}/06.webp'); make(8, s7); f10.result()
subprocess.run(['magick'] + [f'{R}/{k}.webp' for k in ('07', '08', '10')] + ['-resize', '420x', '+append', f'/tmp/claude-501/co{p}.png'])
subprocess.run(['magick'] + [f'{D}/{k}.png' for k in ('07', '08', '10')] + ['-resize', '420x', '+append', f'/tmp/claude-501/cn{p}.png'])
subprocess.run(['magick'] + [f'{D}/{k}-overlay.png' for k in ('07', '08', '10')] + ['+append', f'/tmp/claude-501/cv{p}.png'])
subprocess.run(['magick', f'/tmp/claude-501/co{p}.png', f'/tmp/claude-501/cn{p}.png', f'/tmp/claude-501/cv{p}.png', '-append', f'fin/rich{p}.jpg'])
