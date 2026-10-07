"""Generate the red-oak strip floor texture: python3 oakfloor.py OUT.jpg   (needs numpy, pillow)

2 1/4 in. strips in random lengths, each board with its own tone and grain, drawn so the
image tiles. One tile covers 12 ft square, so nothing visibly repeats within a room.
"""
import sys
import numpy as np
from PIL import Image

N, FEET, STRIP_IN = 2048, 12.0, 2.25
rng = np.random.default_rng(323)
px_per_ft = N / FEET
rows = int(round(FEET * 12 / STRIP_IN))            # 64 strips
sh = N / rows
img = np.zeros((N, N, 3), np.float32)
base = np.array([0.80, 0.585, 0.36])               # honey red oak, as the listing photographs show it


def noise1d(n, scale):
    k = max(2, int(n / scale))
    v = rng.normal(0, 1, k + 1)
    x = np.linspace(0, k, n, endpoint=False)
    i = x.astype(int)
    f = x - i
    f = f * f * (3 - 2 * f)
    return v[i] * (1 - f) + v[(i + 1) % (k + 1)] * f


yy = np.arange(N)
for r in range(rows):
    y0, y1 = int(round(r * sh)), int(round((r + 1) * sh))
    x = int(rng.uniform(0, 3 * px_per_ft))
    start = x
    while x < start + N:
        L = int(rng.uniform(1.0, 5.5) * px_per_ft)
        L = min(L, start + N - x)
        tone = 1 + rng.normal(0, 0.04)
        tint = base * tone * np.array([1 + rng.normal(0, 0.012), 1 + rng.normal(0, 0.01), 1 + rng.normal(0, 0.025)])
        h = y1 - y0
        # grain: fine lines running the length of the board, gently wandering
        lines = np.zeros((h, L), np.float32)
        for _ in range(int(rng.integers(3, 8))):
            c = rng.uniform(0, h) + noise1d(L, 220) * rng.uniform(0.5, 2.5)
            w = rng.uniform(0.5, 1.6)
            lines += np.exp(-((np.arange(h)[:, None] - c[None, :]) ** 2) / (2 * w * w)) * rng.uniform(0.03, 0.10)
        pores = rng.normal(0, 0.018, (h, L)).astype(np.float32)
        pores = (pores + np.roll(pores, 1, 1) + np.roll(pores, 2, 1) + np.roll(pores, 3, 1)) / 2
        shade = 1 - lines + pores + (noise1d(L, 400) * 0.03)[None, :]
        board = tint[None, None, :] * shade[..., None]
        board[:, :1] *= 0.72                         # butt joint
        board[:1, :] *= 0.80                         # edge joint
        cols = (np.arange(x, x + L)) % N
        img[y0:y1, cols] = board
        x += L
Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(sys.argv[1], quality=90)
