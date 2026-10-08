#!/usr/bin/env python3
"""Smoothness of an in-between frame H between neighbors A and B.
detour = (d(A,H) + d(H,B)) / d(A,B): 1.0 means H lies on the straight path from A to B, so it adds no extra change on screen.
off = d(H, blend(A,B)) / d(A,B): how far H is from the plain 50% dissolve."""
import subprocess, sys
def prep(p, out): subprocess.run(['magick', p, '-resize', '640x424!', '-blur', '0x1.5', out], check=True)
def d(a, b):
    r = subprocess.run(['magick', 'compare', '-metric', 'RMSE', a, b, 'null:'], capture_output=True, text=True).stderr
    return float(r.split('(')[1].split(')')[0])
def score(A, H, B, tmp='/tmp/claude-501'):
    a, h, b, m = (f'{tmp}/sm_{x}.png' for x in 'ahbm'); prep(A, a); prep(H, h); prep(B, b)
    subprocess.run(['magick', a, b, '-evaluate-sequence', 'Mean', m], check=True)
    ab = d(a, b); return round((d(a, h) + d(h, b)) / ab, 2), round(d(h, m) / ab, 2), round(ab, 3)
if __name__ == '__main__':
    for p in sys.argv[1:]:
        row = []
        for k in (4, 5, 6, 7, 8, 9):
            det, off, ab = score(f'review/img/{p}/{k:02d}.webp', f'review/img/{p}/{k:02d}h.webp', f'review/img/{p}/{k + 1:02d}.webp'); row.append(f'{k}.5: {det} ({off})')
        print(p, ' | '.join(row))
