"""Project the listing photographs onto the model.

Zillow's 3D tour publishes, for most listing stills, where the camera stood on
the floor plan, which way it faced and its horizontal field of view. With that
pose each photograph can be thrown back onto the surfaces it saw. The result is
one RGBA "photo atlas" per lightmap page, sharing the lightmap's UVs: alpha says
whether a texel is covered by a photograph, and the page shows the photo there
instead of the computed shading.

The published pose is only approximate (no height, no tilt), so refine() first
fits each camera to its photograph: the model's structural edges (room corners,
ceiling lines, door and window openings) are projected into the image and the
pose is nudged until they sit on image edges of the same orientation.
"""
import math, os, time, json
import numpy as np
import bpy
from mathutils import Vector
from mathutils.bvhtree import BVHTree

STRUCTURAL = {"paint", "paint_blue", "paint_salt", "paint_sage", "ceiling", "oakfloor", "carpet", "tile", "siding",
              "deck", "cedar", "fpstone", "walltile", "stone", "hearth"}
# pose corrections: east, south, up (feet), heading, vertical shift, roll (degrees), field-of-view scale
BOUNDS = np.array([1.0, 1.0, 0.9, 2.0, 4.0, 0.5, 0.03])
ZERO = (0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
# Surfaces the photographs are not thrown onto. Floors and ceilings are seen at a
# glancing angle with furniture and fans in front of them, and the block furniture
# does not match the real pieces closely enough to carry their image.
NO_PHOTO = {"oakfloor", "carpet", "tile", "ceiling", "sofa", "pillow", "leather", "walnut", "darkwood", "chairwood", "iron",
            "black", "adirondack", "blueseat", "plant", "terracotta", "porcelain", "deck", "cedar", "roof", "grass", "leaves",
            "gravel", "pavers", "bark", "concrete", "deckstain", "tubshell", "kamado", "granite", "white", "extrim", "siding", "fpstone", "hearth", "stone"}


def load_rgb(path):
    im = bpy.data.images.load(path)
    w, h = im.size
    a = np.empty(w * h * 4, dtype=np.float32)
    im.pixels.foreach_get(a)
    bpy.data.images.remove(im)
    return a.reshape(h, w, 4)[::-1, :, :3].copy()      # row 0 = top of the photograph


def sample(img, u, v):
    """Bilinear lookup; u right, v down, both 0..1."""
    h, w = img.shape[:2]
    x = np.clip(u * w - 0.5, 0, w - 1.001)
    y = np.clip(v * h - 0.5, 0, h - 1.001)
    x0, y0 = x.astype(np.int32), y.astype(np.int32)
    fx, fy = (x - x0)[..., None], (y - y0)[..., None]
    return (img[y0, x0] * (1 - fx) * (1 - fy) + img[y0, x0 + 1] * fx * (1 - fy)
            + img[y0 + 1, x0] * (1 - fx) * fy + img[y0 + 1, x0 + 1] * fx * fy)


class Camera:
    def __init__(self, pid, eye, ang, fov, aspect, tune=ZERO):
        dx, dy, dz, dang, shift, roll, fs = tune
        a, rho = math.radians(ang + dang), math.radians(roll)
        self.id = pid
        self.C = np.array([eye[0] + dx, eye[1] + dy, eye[2] + dz], dtype=np.float64)
        self.f = np.array([math.sin(a), math.cos(a), 0.0])
        r, up = np.array([math.cos(a), -math.sin(a), 0.0]), np.array([0.0, 0.0, 1.0])
        self.r = r * math.cos(rho) + up * math.sin(rho)
        self.up = -r * math.sin(rho) + up * math.cos(rho)
        self.t = math.tan(math.radians(fov) / 2) * (1.0 + fs)
        self.shift = math.tan(math.radians(shift))
        self.aspect = aspect

    def uv(self, d):
        """d = points - C. Returns depth along the view axis and image coordinates (v down)."""
        zc = d @ self.f
        with np.errstate(divide="ignore", invalid="ignore"):
            u = 0.5 + (d @ self.r) / zc / (2 * self.t)
            v = 0.5 - ((d @ self.up) / zc - self.shift) / (2 * self.t) * self.aspect
        return zc, u, v


def occluders(B):
    verts, tris = [], []
    for s in B.surfs:
        if s.page == "fx":
            continue
        o = len(verts)
        verts += [tuple(v) for v in s.verts]
        tris += [(o + a, o + b, o + c) for a, b, c in s.tris]
    return BVHTree.FromPolygons(verts, tris)


def planar(s):
    """Affine map from a surface's lightmap coordinates to (as-drawn) space, or None if it is curved."""
    v0 = np.array([tuple(v) for v in getattr(s, "verts0", s.verts)], dtype=np.float64)
    lm = np.array(s.lm, dtype=np.float64)
    A = np.c_[np.ones(len(lm)), lm]
    coef, _, rank, _ = np.linalg.lstsq(A, v0, rcond=None)
    if rank < 3 or np.abs(A @ coef - v0).max() > 0.02:
        return None
    return coef


# ---------------------------------------------------------------------------- pose refinement
def blur(a, r):
    """Three box passes of radius r: close to a Gaussian, cheap with cumulative sums."""
    for _ in range(3):
        for ax in (0, 1):
            pad = [(0, 0), (0, 0)]
            pad[ax] = (r + 1, r)
            c = np.cumsum(np.pad(a, pad, mode="edge"), axis=ax)
            n = a.shape[ax]
            a = (np.take(c, range(2 * r + 1, 2 * r + 1 + n), axis=ax) - np.take(c, range(0, n), axis=ax)) / (2 * r + 1)
    return a


def gradients(img, r):
    g = blur(img.mean(axis=2), r)
    gx, gy = np.zeros_like(g), np.zeros_like(g)
    gx[:, 1:-1] = g[:, 2:] - g[:, :-2]
    gy[1:-1, :] = g[2:, :] - g[:-2, :]
    return gx, gy


def structural_edges(B, step=0.3):
    """Sample points (and unit directions) along the outlines of walls, floors and ceilings."""
    pts, dirs = [], []
    for s in B.surfs:
        if s.mat not in STRUCTURAL or max(s.w, s.h) < 2.5 or min(s.w, s.h) < 0.5:
            continue
        count = {}
        for t in s.tris:
            for a, b in ((t[0], t[1]), (t[1], t[2]), (t[2], t[0])):
                k = (min(a, b), max(a, b))
                count[k] = count.get(k, 0) + 1
        for (a, b), c in count.items():
            if c != 1:
                continue
            p, q = np.array(s.verts[a]), np.array(s.verts[b])
            L = np.linalg.norm(q - p)
            if L < 1.0:
                continue
            n = max(2, int(L / step))
            for i in range(n):
                pts.append(p + (q - p) * (i + 0.5) / n)
                dirs.append((q - p) / L)
    return np.array(pts), np.array(dirs)


def refine(B, cams, photo_dir, log=print, only=None, debug_dir=None):
    """Fit each camera to its photograph. Returns {id8: tune tuple}."""
    bvh = occluders(B)
    pts, dirs = structural_edges(B)
    log("structural edge samples: %d" % len(pts))
    rng = np.random.default_rng(323)
    out = {}
    for pid, (eye, ang, fov) in cams.items():
        if only and pid[:8] not in only:
            continue
        path = os.path.join(photo_dir, pid + ".jpg")
        if not os.path.exists(path):
            continue
        img = load_rgb(path)
        h2, w2 = img.shape[0] // 2 * 2, img.shape[1] // 2 * 2
        small = img[:h2, :w2].reshape(h2 // 2, 2, w2 // 2, 2, 3).mean(axis=(1, 3))
        maps = [gradients(small, 7), gradients(small, 2)]
        caps = [3.0 * float(np.median(np.hypot(gx_, gy_))) + 1e-6 for gx_, gy_ in maps]
        aspect = img.shape[1] / img.shape[0]
        H, W = small.shape[:2]

        def visible(tune):
            cam = Camera(pid, eye, ang, fov, aspect, tune)
            d = pts - cam.C
            zc, u, v = cam.uv(d)
            dist = np.linalg.norm(d, axis=1)
            cand = np.flatnonzero((zc > 1.0) & (u > -0.15) & (u < 1.15) & (v > -0.15) & (v < 1.15) & (dist < 45))
            keep = []
            Cv = Vector(cam.C)
            for i in cand:
                L = dist[i]
                hit = bvh.ray_cast(Cv, Vector(d[i] / L), L + 0.5)
                if hit[0] is None or hit[3] > L - 0.3:
                    keep.append(i)
            return np.array(keep, dtype=np.int64)

        def score(tune, idx, level):
            cam = Camera(pid, eye, ang, fov, aspect, tune)
            P = pts[idx]
            zc, u, v = cam.uv(P - cam.C)
            zc2, u2, v2 = cam.uv(P + dirs[idx] * 0.3 - cam.C)
            ok = (zc > 0.5) & (zc2 > 0.5) & (u > 0.02) & (u < 0.98) & (v > 0.02) & (v < 0.97) & ~((u < 0.17) & (v > 0.9))
            if ok.sum() < 30:
                return 0.0
            tx, ty = (u2 - u) * W, (v2 - v) * H
            tl = np.hypot(tx, ty) + 1e-9
            nx, ny = -ty / tl, tx / tl
            xi = np.clip((u * W).astype(np.int32), 0, W - 1)
            yi = np.clip((v * H).astype(np.int32), 0, H - 1)
            gx, gy = maps[level]
            # saturate, so a few hard furniture edges cannot outvote many soft wall lines
            resp = np.tanh(np.abs(gx[yi, xi] * nx + gy[yi, xi] * ny) / caps[level])
            return float(np.where(ok, resp, 0).sum() / len(idx))

        best = np.zeros(7)
        idx = visible(tuple(best))
        if len(idx) < 60:
            log("  %s: too few model edges in view, left as published" % pid[:8])
            continue
        base = [score(tuple(best), idx, lv) for lv in (0, 1)]
        for rnd, (level, spread, n) in enumerate(((0, 0.5, 500), (0, 0.2, 400), (1, 0.12, 500), (1, 0.05, 400))):
            if rnd == 2:
                idx2 = visible(tuple(best))               # the view has moved: recompute what it sees
                if len(idx2) >= 60:
                    idx = idx2
            cur = score(tuple(best), idx, level)
            for _ in range(n):
                trial = np.clip(best + rng.normal(0, 1, 7) * BOUNDS * spread * (rng.random(7) < 0.6), -BOUNDS, BOUNDS)
                sc = score(tuple(trial), idx, level)
                if sc > cur:
                    best, cur = trial, sc
        if debug_dir:                                      # published pose in red, fitted pose in green
            os.makedirs(debug_dir, exist_ok=True)
            canvas = np.clip(small * 0.75, 0, 1)
            for tn, colr in ((ZERO, (1, 0, 0)), (tuple(best), (0, 1, 0))):
                cam = Camera(pid, eye, ang, fov, aspect, tn)
                zc, u, v = cam.uv(pts[idx] - cam.C)
                ok = (zc > 0.5) & (u > 0) & (u < 1) & (v > 0) & (v < 1)
                for oy_ in (0, 1):
                    for ox_ in (0, 1):
                        canvas[np.clip((v[ok] * H).astype(int) + oy_, 0, H - 1), np.clip((u[ok] * W).astype(int) + ox_, 0, W - 1)] = colr
            im = bpy.data.images.new("dbg", W, H)
            im.pixels.foreach_set(np.dstack([canvas[::-1], np.ones((H, W))]).astype(np.float32).ravel())
            im.filepath_raw = os.path.join(debug_dir, pid[:8] + ".png")
            im.file_format = "PNG"
            im.save()
            bpy.data.images.remove(im)
        final = score(tuple(best), idx, 1)
        gain = final / max(base[1], 1e-9)
        if gain > 1.12:
            out[pid[:8]] = tuple(round(float(x), 4) for x in best)
            log("  %s fit x%.2f  move %+.2f %+.2f %+.2f ft  turn %+.1f  shift %+.1f  roll %+.1f  fov %+.1f%%"
                % (pid[:8], gain, best[0], best[1], best[2], best[3], best[4], best[5], best[6] * 100))
        else:
            log("  %s: no clear improvement (x%.2f), left as published" % (pid[:8], gain))
    return out


# ---------------------------------------------------------------------------- projection
def project(B, cams, photo_dir, out_dir, size, ycal, log=print, only=None, tune=None, keep=None):
    """cams: {id: (eye feet, heading deg, hfov deg)}. Writes photo_<page>.png into out_dir."""
    tune = tune or {}
    t0 = time.time()
    bvh = occluders(B)
    views = []
    for pid, (eye, ang, fov) in cams.items():
        if only and pid[:8] not in only:
            continue
        path = os.path.join(photo_dir, pid + ".jpg")
        if not os.path.exists(path):
            continue
        img = load_rgb(path)
        cam = Camera(pid, eye, ang, fov, img.shape[1] / img.shape[0], tuple(tune.get(pid[:8], ZERO)))
        cam.img = img
        views.append(cam)
    log("photographs: %d (%d with a fitted pose)" % (len(views), sum(1 for v in views if v.id[:8] in tune)))

    pages = {}
    ycal_v = np.vectorize(ycal, otypes=[np.float64])
    done = skipped = rays = 0
    for s in B.surfs:
        # narrow pieces (rails, balusters, casings) keep their own material
        # (the exterior has too few calibrated photographs to be worth projecting)
        if s.page == "fx" or s.grp == "ex" or s.mat in NO_PHOTO or max(s.w, s.h) < 0.7 or min(s.w, s.h) < 0.45:
            skipped += 1
            continue
        coef = planar(s)
        if coef is None:
            skipped += 1                                  # curved strip: leave it to the material
            continue
        O, U, V = coef
        n = np.cross(U, V)
        nl = np.linalg.norm(n)
        if nl < 1e-9:
            continue
        n /= nl
        if np.dot(n, np.mean([tuple(x) for x in s.nrm], axis=0)) < 0:
            n = -n
        W_, H_ = max(1, int(math.ceil(s.w * s.dens))), max(1, int(math.ceil(s.h * s.dens)))
        aa = (np.arange(W_) + 0.5) / s.dens
        bb = (np.arange(H_) + 0.5) / s.dens
        P = O[None, None, :] + aa[None, :, None] * U[None, None, :] + bb[:, None, None] * V[None, None, :]
        if hasattr(s, "verts0"):  # only hand-drawn surfaces need the plan calibration
            P[..., 1] = ycal_v(P[..., 1])
        k = max(1, int(math.ceil(max(W_, H_) / 150.0)))
        Pc = P[k // 2::k, k // 2::k]
        acc = np.zeros((H_, W_, 3), dtype=np.float32)
        wsum = np.zeros((H_, W_), dtype=np.float32)
        ctr = P[H_ // 2, W_ // 2]
        allow = keep(P) if keep else np.ones((H_, W_), dtype=bool)
        if not allow.any():
            continue
        seen = []                                         # (total weight, camera, full-resolution weight map)
        for cam in views:
            C = cam.C
            if abs(C[2] - ctr[2]) > 16 or np.linalg.norm(ctr[:2] - C[:2]) > 60:
                continue
            if np.dot(n, C - ctr) <= 0.05:               # camera is behind this face
                continue
            d = Pc - C
            zc, u, v = cam.uv(d)
            ok = (zc > 0.6) & (u > 0.015) & (u < 0.985) & (v > 0.02) & (v < 0.98) & ~((u < 0.17) & (v > 0.9))
            if not ok.any():
                continue
            dist = np.linalg.norm(d, axis=-1)
            cosi = -(d @ n) / np.maximum(dist, 1e-6)
            ok &= cosi > 0.3                              # no glancing views: they stretch badly
            idx = np.argwhere(ok)
            if len(idx) == 0:
                continue
            Cv = Vector(C)
            for (j, i) in idx:                            # visibility along the ray from the camera
                L = dist[j, i]
                hit = bvh.ray_cast(Cv, Vector(d[j, i] / L), L + 0.5)
                if hit[0] is not None and hit[3] < L - 0.35:
                    ok[j, i] = False
            rays += len(idx)
            # pull back one sample from every hidden or out-of-frame neighbour: real
            # furniture is rarely exactly where the model's stand-in is
            if ok.shape[0] > 2 and ok.shape[1] > 2:
                e = ok.copy()
                e[1:, :] &= ok[:-1, :]; e[:-1, :] &= ok[1:, :]; e[:, 1:] &= ok[:, :-1]; e[:, :-1] &= ok[:, 1:]
                ok = e
            if not ok.any():
                continue
            edge = np.clip(np.minimum(np.minimum(u, 1 - u), np.minimum(v, 1 - v)) * 10, 0.05, 1)
            wgt = np.where(ok, (np.clip(cosi, 0, 1) ** 1.5) * edge / (1.0 + dist / 12.0) ** 2, 0).astype(np.float32)
            wf = np.repeat(np.repeat(wgt, k, axis=0), k, axis=1)[:H_, :W_]
            if wf.shape != (H_, W_):
                wf = np.pad(wf, ((0, H_ - wf.shape[0]), (0, W_ - wf.shape[1])), mode="edge")
            if wf.any():
                seen.append((float(wf.sum()), cam, wf))
        # One photograph owns the surface (the one that sees it best overall), so a
        # cabinet front or a wall is not stitched from views that disagree by an inch.
        # The others only fill what it could not see.
        for _, cam, wf in sorted(seen, key=lambda t: -t[0]):
            m = (wf > 0) & (wsum == 0) & allow
            if not m.any():
                continue
            zf, uf, vf = cam.uv(P[m] - cam.C)
            inb = (zf > 0.3) & (uf > 0.005) & (uf < 0.995) & (vf > 0.005) & (vf < 0.995)
            col = sample(cam.img, np.clip(uf, 0, 1), np.clip(vf, 0, 1))
            sel = np.zeros_like(m)
            sel[m] = inb
            acc[sel] = col[inb]
            wsum[sel] = wf[m][inb]
        if not (wsum > 0).any():
            continue
        page = pages.setdefault(s.page, np.zeros((size, size, 4), dtype=np.float32))
        x0, y0 = int(s.ox), int(s.oy)
        x1, y1 = min(size, x0 + W_), min(size, y0 + H_)
        cov = wsum > 0
        tile = np.dstack([np.where(cov[..., None], acc, 0), cov.astype(np.float32)])
        page[y0:y1, x0:x1] = tile[: y1 - y0, : x1 - x0]
        done += 1
    log("projected onto %d surfaces (%d left to materials), %d rays, %.0fs" % (done, skipped, rays, time.time() - t0))
    os.makedirs(out_dir, exist_ok=True)
    for name, px in pages.items():
        im = bpy.data.images.new("photo_" + name, size, size, alpha=True)
        im.colorspace_settings.name = "Non-Color"
        im.alpha_mode = "STRAIGHT"
        im.pixels.foreach_set(px.ravel())
        im.filepath_raw = os.path.join(out_dir, "photo_%s.png" % name)
        im.file_format = "PNG"
        im.save()
        log("photo atlas", name, "coverage %.1f%%" % (100 * (px[..., 3] > 0).mean()))
    return sorted(pages)
