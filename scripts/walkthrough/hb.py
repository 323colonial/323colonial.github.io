"""Geometry builder for the 323 Colonial walkthrough model.

Plain-Python mesh accumulator used by house.py (run inside Blender).
World frame, in feet: X = west of the east exterior wall face, Y = south of the
north (front) exterior wall face, Z = up from the main finished floor. That is a
right-handed frame, and it is the frame of the A-4 / A-5 sheets as drawn.

Every surface carries two UV sets: uv0 tiles the material in world scale, uv1
is a private rectangle in a lightmap atlas page (packed in pack()).
"""
import math
from mathutils import Vector
from mathutils.geometry import delaunay_2d_cdt

UP = Vector((0, 0, 1))


class Surf:
    __slots__ = ("mat", "grp", "verts", "tris", "uv0", "lm", "nrm", "w", "h", "page", "ox", "oy", "dens", "pw", "ph", "node", "verts0")


class Builder:
    def __init__(self):
        self.surfs = []
        self.solids = []   # collision: (x0, y0, x1, y1, zmin, zmax)
        self.floors = []   # walkable: dict(poly=[(x, y)...], z=float) or ramp
        self.doors = []    # swinging doors: dict(name, hinge, open, seg, z0, z1)
        self.lights = []   # (x, y, z, relative power)
        self.downlights = {}  # recessed light index -> aperture radius in feet
        self.mats = {}
        self.grp = "in"
        self.dens = 20.0   # lightmap texels per foot

    # ---- generic planar polygon -------------------------------------------------
    def poly(self, mat, pts, holes=(), grp=None, dens=None, fit=None, uvrot=False, flip=False):
        """pts: 3D points, counter-clockwise seen from the visible side.
        fit: None for world-scale tiling, or (umin, vmin, umax, vmax) to stretch
        that sub-rectangle of the texture over the polygon's bounding box."""
        pts = [Vector(p) for p in pts]
        if flip:
            pts = pts[::-1]
        n = Vector((0, 0, 0))
        for i in range(len(pts)):
            n += pts[i].cross(pts[(i + 1) % len(pts)])
        if n.length < 1e-9:
            return None
        n.normalize()
        if abs(n.z) > 0.999:
            U = Vector((1, 0, 0))
        else:
            U = UP.cross(n).normalized()
        V = n.cross(U)
        allpts = list(pts)
        loops = [pts]
        for h in holes:
            h = [Vector(p) for p in h]
            loops.append(h)
            allpts += h
        if len(loops) == 1 and len(pts) == 4:
            tris = [(0, 1, 2), (0, 2, 3)]
        elif len(loops) == 1 and len(pts) == 3:
            tris = [(0, 1, 2)]
        else:
            # constrained Delaunay handles holes robustly; it may add or merge vertices
            o = pts[0]
            co, faces, k = [], [], 0
            for li, lp in enumerate(loops):
                c2 = [Vector(((p - o).dot(U), (p - o).dot(V))) for p in lp]
                area = sum(c2[i].x * c2[(i + 1) % len(c2)].y - c2[(i + 1) % len(c2)].x * c2[i].y for i in range(len(c2)))
                if (area > 0) != (li == 0):   # outer loop CCW, holes CW
                    c2.reverse()
                co += c2
                faces.append(list(range(k, k + len(lp))))
                k += len(lp)
            ov, _, of, _, _, _ = delaunay_2d_cdt(co, [], faces, 3, 1e-5)
            allpts = [o + U * v.x + V * v.y for v in ov]
            tris = []
            for f in of:
                for i in range(1, len(f) - 1):
                    t = (f[0], f[i], f[i + 1])
                    a_, b_, c_ = (allpts[j] for j in t)
                    if (b_ - a_).cross(c_ - a_).dot(n) < 0:
                        t = (t[0], t[2], t[1])
                    tris.append(t)
        s = Surf()
        s.mat, s.grp, s.verts, s.tris = mat, grp or self.grp, allpts, tris
        us = [p.dot(U) for p in allpts]
        vs = [p.dot(V) for p in allpts]
        u0, v0 = min(us), min(vs)
        s.w, s.h = max(us) - u0, max(vs) - v0
        s.lm = [(u - u0, v - v0) for u, v in zip(us, vs)]
        if fit:
            fu0, fv0, fu1, fv1 = fit
            s.uv0 = [(fu0 + (fu1 - fu0) * a / max(s.w, 1e-6), fv0 + (fv1 - fv0) * b / max(s.h, 1e-6)) for a, b in s.lm]
        else:
            t = self.mats.get(mat, {}).get("tile", 4.0)
            if uvrot:
                s.uv0 = [(v / t, -u / t) for u, v in zip(us, vs)]
            else:
                s.uv0 = [(u / t, v / t) for u, v in zip(us, vs)]
        s.nrm = [n] * len(allpts)
        s.dens = dens or self.dens
        self.surfs.append(s)
        return s

    def quad(self, mat, a, b, c, d, **kw):
        return self.poly(mat, [a, b, c, d], **kw)

    # ---- boxes ------------------------------------------------------------------
    def box(self, mat, x0, y0, z0, x1, y1, z1, skip="", mats=None, **kw):
        """Axis-aligned box. skip: any of 'x-','x+','y-','y+','z-','z+' faces to omit.
        mats: optional per-face material override dict keyed like skip."""
        if x1 < x0: x0, x1 = x1, x0
        if y1 < y0: y0, y1 = y1, y0
        if z1 < z0: z0, z1 = z1, z0
        m = lambda k: (mats or {}).get(k, mat)
        P = lambda x, y, z: (x, y, z)
        if "z+" not in skip: self.quad(m("z+"), P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1), **kw)
        if "z-" not in skip: self.quad(m("z-"), P(x0, y1, z0), P(x1, y1, z0), P(x1, y0, z0), P(x0, y0, z0), **kw)
        if "y-" not in skip: self.quad(m("y-"), P(x1, y0, z0), P(x1, y0, z1), P(x0, y0, z1), P(x0, y0, z0), **kw)
        if "y+" not in skip: self.quad(m("y+"), P(x0, y1, z0), P(x0, y1, z1), P(x1, y1, z1), P(x1, y1, z0), **kw)
        if "x-" not in skip: self.quad(m("x-"), P(x0, y0, z0), P(x0, y0, z1), P(x0, y1, z1), P(x0, y1, z0), **kw)
        if "x+" not in skip: self.quad(m("x+"), P(x1, y1, z0), P(x1, y1, z1), P(x1, y0, z1), P(x1, y0, z0), **kw)

    def obox(self, mat, o, ax, ay, az, skip="", **kw):
        """Oriented box from origin corner o and three edge vectors (right-handed)."""
        o, ax, ay, az = Vector(o), Vector(ax), Vector(ay), Vector(az)
        c = lambda i, j, k: o + ax * i + ay * j + az * k
        if "z+" not in skip: self.quad(mat, c(0, 0, 1), c(1, 0, 1), c(1, 1, 1), c(0, 1, 1), **kw)
        if "z-" not in skip: self.quad(mat, c(0, 1, 0), c(1, 1, 0), c(1, 0, 0), c(0, 0, 0), **kw)
        if "y-" not in skip: self.quad(mat, c(1, 0, 0), c(1, 0, 1), c(0, 0, 1), c(0, 0, 0), **kw)
        if "y+" not in skip: self.quad(mat, c(0, 1, 0), c(0, 1, 1), c(1, 1, 1), c(1, 1, 0), **kw)
        if "x-" not in skip: self.quad(mat, c(0, 0, 0), c(0, 0, 1), c(0, 1, 1), c(0, 1, 0), **kw)
        if "x+" not in skip: self.quad(mat, c(1, 1, 0), c(1, 1, 1), c(1, 0, 1), c(1, 0, 0), **kw)

    def beam(self, mat, a, b, w, h, **kw):
        """Rectangular bar between two points; w horizontal width, h height (centred)."""
        a, b = Vector(a), Vector(b)
        d = b - a
        L = d.length
        d.normalize()
        side = UP.cross(d)
        if side.length < 1e-6:
            side = Vector((1, 0, 0))
        side.normalize()
        up = d.cross(side)
        self.obox(mat, a - side * w / 2 - up * h / 2, d * L, side * w, up * h, **kw)

    # ---- smooth strips: lathe and cylinder ------------------------------------------
    def lathe(self, mat, c, profile, n=20, grp=None, dens=None, a0=0.0, a1=2 * math.pi):
        """Revolve profile [(r, z), ...] about the vertical axis through c=(x, y)."""
        s = Surf()
        s.mat, s.grp, s.dens = mat, grp or self.grp, dens or self.dens
        s.verts, s.tris, s.uv0, s.lm, s.nrm = [], [], [], [], []
        rmax = max(r for r, _ in profile)
        lens = [0.0]
        for i in range(1, len(profile)):
            lens.append(lens[-1] + math.hypot(profile[i][0] - profile[i - 1][0], profile[i][1] - profile[i - 1][1]))
        m = len(profile)
        t = self.mats.get(mat, {}).get("tile", 4.0)
        for j in range(n + 1):
            a = a0 + (a1 - a0) * j / n
            ca, sa = math.cos(a), math.sin(a)
            for i, (r, z) in enumerate(profile):
                s.verts.append(Vector((c[0] + r * ca, c[1] + r * sa, z)))
                k0, k1 = max(i - 1, 0), min(i + 1, m - 1)
                dr, dz = profile[k1][0] - profile[k0][0], profile[k1][1] - profile[k0][1]
                nn = Vector((dz * ca, dz * sa, -dr))
                s.nrm.append(nn.normalized() if nn.length > 1e-9 else UP)
                u = rmax * (a - a0)
                s.lm.append((u, lens[i]))
                s.uv0.append((u / t, lens[i] / t))
        for j in range(n):
            for i in range(m - 1):
                a, b, cc, d = j * m + i, (j + 1) * m + i, (j + 1) * m + i + 1, j * m + i + 1
                s.tris += [(a, b, cc), (a, cc, d)]
        s.w, s.h = rmax * (a1 - a0), lens[-1]
        self.surfs.append(s)
        return s

    def cyl(self, mat, c, r, z0, z1, n=16, caps=True, **kw):
        prof = [(r, z0), (r, z1)]
        self.lathe(mat, c, prof, n=n, **kw)
        if caps:
            ring = [(c[0] + r * math.cos(2 * math.pi * j / n), c[1] + r * math.sin(2 * math.pi * j / n)) for j in range(n)]
            self.poly(mat, [(x, y, z1) for x, y in ring], **kw)
            self.poly(mat, [(x, y, z0) for x, y in ring[::-1]], **kw)

    def tube(self, mat, a, b, r, n=8, **kw):
        """Smooth cylinder between two arbitrary points (no caps)."""
        a, b = Vector(a), Vector(b)
        d = (b - a)
        L = d.length
        d.normalize()
        side = d.cross(UP)
        if side.length < 1e-6:
            side = Vector((1, 0, 0))
        side.normalize()
        up = side.cross(d)
        s = Surf()
        s.mat, s.grp, s.dens = mat, kw.get("grp") or self.grp, kw.get("dens") or self.dens
        s.verts, s.tris, s.uv0, s.lm, s.nrm = [], [], [], [], []
        t = self.mats.get(mat, {}).get("tile", 4.0)
        for j in range(n + 1):
            ang = 2 * math.pi * j / n
            nn = side * math.cos(ang) + up * math.sin(ang)
            for k, p in enumerate((a, b)):
                s.verts.append(p + nn * r)
                s.nrm.append(nn)
                s.lm.append((r * ang, k * L))
                s.uv0.append((r * ang / t, k * L / t))
        for j in range(n):
            i = j * 2
            s.tris += [(i, i + 2, i + 3), (i, i + 3, i + 1)]
        s.w, s.h = 2 * math.pi * r, L
        self.surfs.append(s)

    # ---- collision / walkable bookkeeping -------------------------------------------
    def solid(self, x0, y0, x1, y1, z0=0.0, z1=8.0):
        self.solids.append((x0, y0, x1, y1, z0, z1))

    def solid_box(self, x0, y0, x1, y1, z0=0.0, z1=8.0):
        for s in ((x0, y0, x1, y0), (x1, y0, x1, y1), (x1, y1, x0, y1), (x0, y1, x0, y0)):
            self.solids.append(s + (z0, z1))

    def floor(self, poly, z):
        self.floors.append({"poly": [list(p) for p in poly], "z": z})

    # ---- lightmap packing --------------------------------------------------------------
    def pack(self, size=4096, pad=4):
        """Shelf-pack every surface's rectangle into atlas pages per group."""
        pages = {}
        by = {}
        for s in self.surfs:
            by.setdefault(s.grp, []).append(s)
        for grp, lst in by.items():
            if grp == "fx":
                for s in lst:
                    s.page, s.ox, s.oy = "fx", 0, 0
                pages["fx"] = 0
                continue
            for s in lst:
                s.pw = max(2, int(math.ceil(s.w * s.dens))) + 2 * pad
                s.ph = max(2, int(math.ceil(s.h * s.dens))) + 2 * pad
                if s.pw > size or s.ph > size:
                    k = max(s.pw, s.ph) / float(size - 1)
                    s.dens /= k * 1.02
                    s.pw = max(2, int(math.ceil(s.w * s.dens))) + 2 * pad
                    s.ph = max(2, int(math.ceil(s.h * s.dens))) + 2 * pad
            lst.sort(key=lambda s: -s.ph)
            page, x, y, rowh = 0, 0, 0, 0
            for s in lst:
                if x + s.pw > size:
                    x, y, rowh = 0, y + rowh, 0
                if y + s.ph > size:
                    page, x, y, rowh = page + 1, 0, 0, 0
                s.page, s.ox, s.oy = "%s%d" % (grp, page), x + pad, y + pad
                x += s.pw
                rowh = max(rowh, s.ph)
            pages[grp] = page + 1
        self.size = size
        return pages

    def uv1(self, s):
        if s.page == "fx":
            return [(0.0, 0.0)] * len(s.verts)
        sz = float(self.size)
        return [((s.ox + a * s.dens) / sz, (s.oy + b * s.dens) / sz) for a, b in s.lm]


class Wall:
    """Vertical wall along a plan segment with openings; see Builder-based helpers.

    a -> b is the run direction; the 'L' face is on the left of that direction
    (normal = (-dy, dx)), the 'R' face on the right. Openings are in (s, z)."""

    def __init__(self, B, a, b, z0, z1, t=0.375, mL="paint", mR="paint", top=None, grp=None, grpR=None,
                 solid=True, ends=True):
        self.B, self.a, self.b = B, Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
        d = self.b - self.a
        self.L = d.length
        self.d = d.normalized()
        self.n = Vector((-self.d.y, self.d.x, 0))
        self.z0, self.z1, self.t, self.mL, self.mR = z0, z1, t, mL, mR
        self.top = top   # optional [(s, z), ...] top profile from s=0 to s=L
        self.grpL, self.grpR = grp, grpR or grp
        self.holes = []  # (poly in (s, z), passable)
        self.is_solid, self.ends = solid, ends

    def pt(self, s, z, off=0.0):
        return self.a + self.d * s + self.n * off + UP * z

    def hole(self, s0, s1, z0, z1):
        self.holes.append(([(s0, z0), (s1, z0), (s1, z1), (s0, z1)], z0 <= self.z0 + 0.6 and z1 - z0 > 5.5, (s0, s1)))
        return (s0, s1, z0, z1)

    def hole_poly(self, pts):
        ss = [p[0] for p in pts]
        self.holes.append((list(pts), False, (min(ss), max(ss))))

    def build(self):
        B, h = self.B, self.t / 2
        prof = self.top or [(0, self.z1), (self.L, self.z1)]
        outline = [(0, self.z0), (self.L, self.z0)] + list(reversed(prof))
        for side, mat, grp in ((1, self.mL, self.grpL), (-1, self.mR, self.grpR)):
            if mat is None:
                continue
            outer = [self.pt(s, z, side * h) for s, z in outline]
            holes = [[self.pt(s, z, side * h) for s, z in hp] for hp, _, _ in self.holes]
            if side > 0:
                outer = outer[::-1]
            B.poly(mat, outer, holes=holes, grp=grp)
        # reveals inside every opening
        for hp, _, _ in self.holes:
            m = len(hp)
            for i in range(m):
                (s0, za), (s1, zb) = hp[i], hp[(i + 1) % m]
                if max(za, zb) <= self.z0 + 0.02:
                    continue                            # no threshold strip lying in the floor
                # one face only: the page draws both sides, and a coincident pair flickers
                B.quad("trim", self.pt(s0, za, -h), self.pt(s0, za, h), self.pt(s1, zb, h), self.pt(s1, zb, -h),
                       grp=self.grpL)
        if self.ends:
            zt0, zt1 = prof[0][1], prof[-1][1]
            if self.mL:
                B.quad(self.mL, self.pt(0, self.z0, h), self.pt(0, self.z0, -h), self.pt(0, zt0, -h), self.pt(0, zt0, h), grp=self.grpL)
                B.quad(self.mL, self.pt(self.L, self.z0, -h), self.pt(self.L, self.z0, h), self.pt(self.L, zt1, h), self.pt(self.L, zt1, -h), grp=self.grpL)
        # top cap
        if self.mL:
            for (s0, za), (s1, zb) in zip(prof, prof[1:]):
                B.quad(self.mL, self.pt(s0, za, -h), self.pt(s1, zb, -h), self.pt(s1, zb, h), self.pt(s0, za, h), grp=self.grpL)
        # collision: the solid runs between passable openings
        if self.is_solid:
            cuts = sorted(rng for _, passable, rng in self.holes if passable)
            s = 0.0
            for c0, c1 in cuts + [(self.L, self.L)]:
                if c0 - s > 0.05:
                    p, q = self.pt(s, 0), self.pt(c0, 0)
                    B.solid(p.x, p.y, q.x, q.y, self.z0, max(z for _, z in prof))
                s = c1
        return self
