#!/usr/bin/env python3
"""Fit one affine correction per generated frame from fixed-structure edge patches, ImageMagick only.
usage: align.py MASTER GENERATED OUT.png  -> prints fit summary as JSON"""
import json, os, re, subprocess, sys, tempfile
P, R = 112, 14          # patch size, search radius (px at master scale)
EDGE = ['-colorspace', 'Gray', '-canny', '0x1+8%+22%', '-blur', '0x1.2']

def run(*a): return subprocess.run(a, capture_output=True, text=True)

def measure(master, gen, tmp):
    w, h = map(int, run('magick', 'identify', '-format', '%w %h', master).stdout.split())
    me, ge = f'{tmp}/m.png', f'{tmp}/g.png'
    run('magick', master, *EDGE, me); run('magick', gen, *EDGE, ge)
    pts = [(x, y) for y in range(R + 8, h - P - R - 8, (h - P - 2 * R - 16) // 6) for x in range(R + 8, w - P - R - 8, (w - P - 2 * R - 16) // 9)]
    def one(i):
        x, y = pts[i]; a, b = f'{tmp}/p{i}.png', f'{tmp}/s{i}.png'
        run('magick', me, '-crop', f'{P}x{P}+{x}+{y}', '+repage', a)
        m = run('magick', a, '-format', '%[fx:mean]', 'info:').stdout
        if float(m or 0) < 0.035: return None                      # too little structure
        run('magick', ge, '-crop', f'{P + 2 * R}x{P + 2 * R}+{x - R}+{y - R}', '+repage', b)
        r = run('magick', 'compare', '-metric', 'NCC', '-subimage-search', b, a, 'null:').stderr
        g = re.search(r'([\d.eE+-]+)\s*(?:\(([\d.]+)\))?\s*@\s*(-?\d+),(-?\d+)', r)
        if not g: return None
        return (x + P / 2, y + P / 2, int(g.group(3)) - R, int(g.group(4)) - R, float(g.group(2) or g.group(1)))
    # Frame-level callers own parallelism; nested patch pools multiply ImageMagick processes.
    res = [r for r in map(one, range(len(pts))) if r]
    return w, h, res

def solve3(A, b):
    n = 3; M = [A[i][:] + [b[i]] for i in range(n)]
    for i in range(n):
        p = max(range(i, n), key=lambda r: abs(M[r][i])); M[i], M[p] = M[p], M[i]
        if abs(M[i][i]) < 1e-12: return None
        for r in range(n):
            if r != i:
                f = M[r][i] / M[i][i]; M[r] = [M[r][c] - f * M[i][c] for c in range(n + 1)]
    return [M[i][n] / M[i][i] for i in range(n)]

def fit(res):
    def ls(rows, k):
        A = [[0.0] * 3 for _ in range(3)]; b = [0.0] * 3
        for r in rows:
            v = (r[0], r[1], 1.0)
            for i in range(3):
                b[i] += v[i] * r[k]
                for j in range(3): A[i][j] += v[i] * v[j]
        return solve3(A, b)
    rows = [r for r in res if abs(r[2]) < R and abs(r[3]) < R]      # drop matches pinned at the search edge
    for _ in range(6):
        if len(rows) < 6: return None, rows
        fx, fy = ls(rows, 2), ls(rows, 3)
        if not fx or not fy: return None, rows
        err = [((fx[0] * r[0] + fx[1] * r[1] + fx[2] - r[2]) ** 2 + (fy[0] * r[0] + fy[1] * r[1] + fy[2] - r[3]) ** 2) ** .5 for r in rows]
        keep = [r for r, e in zip(rows, err) if e <= max(1.0, 1.5 * sorted(err)[len(err) // 2])]
        if len(keep) == len(rows): break
        rows = keep
    return (fx, fy), rows

def main(master, gen, out):
    with tempfile.TemporaryDirectory() as tmp:
        w, h, res = measure(master, gen, tmp)
        f, rows = fit(res)
        info = {'patches': len(res), 'inliers': len(rows)}
        if f and len(rows) < 12: f = None          # too few matching edges to trust a correction; applying one can stretch the frame
        if not f:
            run('magick', gen, out); info['applied'] = False; print(json.dumps(info)); return
        fx, fy = f
        d = lambda x, y: (fx[0] * x + fx[1] * y + fx[2], fy[0] * x + fy[1] * y + fy[2])
        corners = [(0, 0), (w, 0), (0, h), (w, h)]
        info['corner_shift_px'] = [[round(v, 2) for v in d(*c)] for c in corners]
        info['max_shift_px'] = round(max((dx * dx + dy * dy) ** .5 for dx, dy in map(lambda c: d(*c), corners)), 2)
        cp = ' '.join(f'{x + d(x, y)[0]:.3f},{y + d(x, y)[1]:.3f} {x},{y}' for x, y in corners[:3])   # generated -> master
        run('magick', gen, '-virtual-pixel', 'mirror', '-filter', 'Lanczos', '-distort', 'Affine', cp, '+repage', out)
        # residual after correction, same patches
        w2, h2, res2 = measure(master, out, tmp)
        good = [(r[2] ** 2 + r[3] ** 2) ** .5 for r in res2 if any(abs(r[0] - q[0]) < 1 and abs(r[1] - q[1]) < 1 for q in rows)]
        info['residual_median_px'] = round(sorted(good)[len(good) // 2], 2) if good else None
        info['residual_max_px'] = round(max(good), 2) if good else None
        info['applied'] = True; print(json.dumps(info))
if __name__ == '__main__': main(*sys.argv[1:4])
