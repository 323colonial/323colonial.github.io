"""Reusable building parts (windows, doors, rails, cabinets) on top of hb.Builder."""
import math
from mathutils import Vector, Matrix
from hb import Wall, UP


def wbox(B, w, mat, s0, s1, z0, z1, o0, o1, **kw):
    """Box in a wall's frame: along run s, height z, offset o across the wall."""
    if s1 < s0: s0, s1 = s1, s0
    if z1 < z0: z0, z1 = z1, z0
    if o1 < o0: o0, o1 = o1, o0
    B.obox(mat, w.pt(s0, z0, o0), w.d * (s1 - s0), w.n * (o1 - o0), UP * (z1 - z0), **kw)


def casing(B, w, s0, s1, z0, z1, side, mat="oak", wd=0.3, th=0.07, sill=True, grp=None):
    """Picture-frame casing on one face of the wall (side = +1 for L, -1 for R)."""
    a = side * w.t / 2
    b = a + side * th
    wbox(B, w, mat, s0 - wd, s0, z0, z1 + wd, a, b, grp=grp)
    wbox(B, w, mat, s1, s1 + wd, z0, z1 + wd, a, b, grp=grp)
    wbox(B, w, mat, s0, s1, z1, z1 + wd, a, b, grp=grp)
    if mat in ("oak", "trim"):
        c = a + side * (th + 0.035)
        for sa in (s0 - wd - 0.03, s1 - 0.03):                      # rosette blocks
            wbox(B, w, mat, sa, sa + wd + 0.06, z1 - 0.03, z1 + wd + 0.03, a, c, grp=grp)
            wbox(B, w, mat, sa + 0.1, sa + wd - 0.04, z1 + 0.07, z1 + wd - 0.07, c, c + side * 0.02, grp=grp)
        for sa in (s0 - wd, s1):                                    # a raised bead down each leg
            wbox(B, w, mat, sa + wd / 2 - 0.035, sa + wd / 2 + 0.035, z0 + (0.0 if sill else 0.5), z1 - 0.03, b, b + side * 0.018, grp=grp)
        if not sill:
            for sa in (s0 - wd - 0.02, s1 - 0.02):                  # plinth blocks
                wbox(B, w, mat, sa, sa + wd + 0.04, z0, z0 + 0.5, a, c, grp=grp)
    if sill:
        wbox(B, w, mat, s0 - wd, s1 + wd, z0 - wd, z0, a, b, grp=grp)
        wbox(B, w, mat, s0 - wd - 0.05, s1 + wd + 0.05, z0 - 0.07, z0, a, a + side * 0.22, grp=grp)


def glazing(B, w, s0, s1, z0, z1, grid=(3, 2), frame="winframe", fw=0.13, bar=0.045, grp_out="ex"):
    """One glazed sash: perimeter frame, glass pane and muntin bars."""
    d = 0.16
    for a, b, c, e in ((s0, s0 + fw, z0, z1), (s1 - fw, s1, z0, z1), (s0 + fw, s1 - fw, z0, z0 + fw), (s0 + fw, s1 - fw, z1 - fw, z1)):
        wbox(B, w, frame, a, b, c, e, -d, d, grp=grp_out)
    B.quad("glass", w.pt(s0 + fw, z0 + fw, 0), w.pt(s1 - fw, z0 + fw, 0), w.pt(s1 - fw, z1 - fw, 0), w.pt(s0 + fw, z1 - fw, 0), grp="fx")
    nx, ny = grid
    for i in range(1, nx):
        s = s0 + fw + (s1 - s0 - 2 * fw) * i / nx
        wbox(B, w, frame, s - bar / 2, s + bar / 2, z0 + fw, z1 - fw, -0.04, 0.04, grp=grp_out)
    for j in range(1, ny):
        z = z0 + fw + (z1 - z0 - 2 * fw) * j / ny
        wbox(B, w, frame, s0 + fw, s1 - fw, z - bar / 2, z + bar / 2, -0.04, 0.04, grp=grp_out)


def window(B, w, s0, s1, z0, z1, units=1, hung=True, grid=(3, 2), inside=1, grp_in=None, extrim="extrim", shelf=None):
    """Punch and fill a window. units: side-by-side sashes; hung: split each at mid height."""
    w.hole(s0, s1, z0, z1)
    mull = 0.25
    uw = (s1 - s0 - mull * (units - 1)) / units
    for u in range(units):
        a = s0 + u * (uw + mull)
        if u:
            wbox(B, w, "oak" if inside else "winframe", a - mull, a, z0, z1, -0.2, 0.2, grp=grp_in)
        if hung:
            zm = (z0 + z1) / 2
            glazing(B, w, a, a + uw, z0, zm + 0.06, grid)
            glazing(B, w, a, a + uw, zm - 0.06, z1, grid)
        else:
            glazing(B, w, a, a + uw, z0, z1, grid)
    if inside:
        casing(B, w, s0, s1, z0, z1, inside, grp=grp_in)
        if shelf:
            a = inside * w.t / 2
            wbox(B, w, "oak", s0 - 0.8, s1 + 0.8, shelf, shelf + 0.09, a, a + inside * 0.55, grp=grp_in)
            for s in (s0 + 0.3, s1 - 0.3):
                wbox(B, w, "oak", s - 0.05, s + 0.05, shelf - 0.45, shelf, a, a + inside * 0.4, grp=grp_in)
    if extrim:
        casing(B, w, s0, s1, z0, z1, -inside if inside else -1, mat=extrim, wd=0.28, th=0.08, grp="ex")


def poly_window(B, w, pts, inside=1, grp_in=None, extrim="extrim"):
    """Fixed glazing of arbitrary outline (the gable trapezoids). pts in (s, z)."""
    w.hole_poly(pts)
    B.poly("glass", [w.pt(s, z, 0) for s, z in pts], grp="fx")
    n = len(pts)
    cs = sum(p[0] for p in pts) / n
    cz = sum(p[1] for p in pts) / n

    def bar(mat, p, q, o0, o1, wd, inward, grp):
        """Board along edge p-q, wd wide in the wall plane, spanning offsets o0..o1."""
        ex, ez = q[0] - p[0], q[1] - p[1]
        L = math.hypot(ex, ez)
        ex, ez = ex / L, ez / L
        nx, nz = ez, -ex
        if (nx * (p[0] - cs) + nz * (p[1] - cz) < 0) != inward:
            nx, nz = -nx, -nz
        ext = 0.0 if inward else wd
        e3 = w.d * ex + UP * ez
        q3 = w.d * nx + UP * nz
        o = w.pt(p[0], p[1], min(o0, o1)) - e3 * ext
        ax, ay, az = e3 * (L + 2 * ext), q3 * wd, w.n * abs(o1 - o0)
        if ax.cross(ay).dot(az) < 0:
            o, ay = o + ay, -ay
        B.obox(mat, o, ax, ay, az, grp=grp)

    for i in range(n):
        p, q = pts[i], pts[(i + 1) % n]
        a = inside * w.t / 2
        bar("oak", p, q, a, a + inside * 0.07, 0.3, False, grp_in)
        bar(extrim, p, q, -a, -a - inside * 0.08, 0.28, False, "ex")
        bar("winframe", p, q, -0.12, 0.12, 0.1, True, "ex")


def door(B, w, s0, s1, z1=6.75, swing=1, hinge="lo", angle=0.0, mat="oakdoor", mat_back=None, case=(1, -1),
         case_mat="oak", grp=None, grp_back=None, z0=0.0, th=0.14, solid=None, glass=None):
    """Punch a door opening and hang a slab. swing: side it opens toward (+1 L, -1 R).
    angle in degrees from closed. glass: optional (u0, u1, v0, v1) fraction of slab for a lite."""
    w.hole(s0, s1, z0, z1)
    for side in case:
        casing(B, w, s0, s1, z0, z1, side, mat=case_mat, sill=False, grp=grp if side > 0 else (grp_back or grp))
    wd = s1 - s0 - 0.04
    sh = s0 + 0.02 if hinge == "lo" else s1 - 0.02
    dirc = w.d if hinge == "lo" else -w.d
    hp = w.pt(sh, z0 + 0.03, 0)
    # Slabs are built closed. A door given an open angle becomes its own node,
    # which the page swings about the hinge when the player comes near.
    ang = math.radians(angle) * swing * (1 if hinge == "lo" else -1)
    ax = dirc.copy()
    n0 = len(B.surfs)
    nn = Vector((-ax.y, ax.x, 0))
    H = z1 - z0 - 0.05
    c = lambda u, v, o: hp + ax * (u * wd) + nn * o + UP * (v * H)
    front, back = th / 2, -th / 2
    mb = mat_back or mat
    fitF, fitB = (0, 0, 1, 1), (1, 0, 0, 1)
    B.poly(mat, [c(0, 0, front), c(0, 1, front), c(1, 1, front), c(1, 0, front)], grp=grp, fit=fitF, flip=False)
    B.poly(mb, [c(1, 0, back), c(1, 1, back), c(0, 1, back), c(0, 0, back)], grp=grp_back or grp, fit=fitB)
    edge = "oak" if mat == "oakdoor" else "white"
    B.quad(edge, c(1, 0, front), c(1, 1, front), c(1, 1, back), c(1, 0, back), grp=grp)
    B.quad(edge, c(0, 0, back), c(0, 1, back), c(0, 1, front), c(0, 0, front), grp=grp)
    B.quad(edge, c(0, 1, front), c(0, 1, back), c(1, 1, back), c(1, 1, front), grp=grp)
    # lever handles
    for o in (front, back):
        sgn = 1 if o > 0 else -1
        k = c(0.92, 0.47, o)
        B.beam("black", k, k + nn * sgn * 0.2, 0.05, 0.05, grp=grp)
        B.beam("black", k + nn * sgn * 0.2, k + nn * sgn * 0.2 - ax * 0.35, 0.05, 0.05, grp=grp)
    p, q = w.pt(s0, 0), w.pt(s1, 0)
    if angle:
        name = "door_%d" % len(B.doors)
        for sf in B.surfs[n0:]:
            sf.node = name
        B.doors.append(dict(name=name, hinge=(hp.x, hp.y), open=ang, seg=(p.x, p.y, q.x, q.y), z0=z0, z1=z1))
    else:
        B.solid(p.x, p.y, q.x, q.y, z0, z1)


def rail(B, a, b, h=3.0, mat="oak", top=(0.22, 0.14), bal=0.1, spacing=0.42, newel=0.3, newels=(True, True),
         bottom=0.28, grp=None, cap=0.35, solid=True):
    """Guard rail from a to b (3D points at walking surface level; may slope)."""
    a, b = Vector(a), Vector(b)
    d = b - a
    L = Vector((d.x, d.y, 0)).length
    B.beam(mat, a + UP * h, b + UP * h, top[0], top[1], grp=grp)
    B.beam(mat, a + UP * bottom, b + UP * bottom, top[0] * 0.8, 0.1, grp=grp)
    n = max(1, int(round(L / spacing)))
    for i in range(1, n):
        p = a + d * (i / n)
        B.box(mat, p.x - bal / 2, p.y - bal / 2, p.z + bottom, p.x + bal / 2, p.y + bal / 2, p.z + h - top[1] / 2,
              skip="z+z-", grp=grp, dens=6)
    for flag, p in zip(newels, (a, b)):
        if flag:
            B.box(mat, p.x - newel / 2, p.y - newel / 2, p.z, p.x + newel / 2, p.y + newel / 2, p.z + h + cap, skip="z-", grp=grp)
    if solid:
        B.solid(a.x, a.y, b.x, b.y, min(a.z, b.z), max(a.z, b.z) + h)


def cabinet_run(B, x0, y0, x1, y1, z0, z1, face, n, mat="oak", grp=None, drawers=False, kick=0.3, top=None, pulls=True):
    """Box of cabinets with n raised door fronts on one face ('x-','x+','y-','y+')."""
    base = z0 == 0
    zb = z0 + (kick if base else 0)
    B.box(mat, x0, y0, zb, x1, y1, z1, grp=grp)
    if base:
        k = 0.2
        kx0, ky0, kx1, ky1 = x0, y0, x1, y1
        if face == "x-": kx0 += k
        if face == "x+": kx1 -= k
        if face == "y-": ky0 += k
        if face == "y+": ky1 -= k
        B.box("black", kx0, ky0, 0, kx1, ky1, zb, skip="z+z-", grp=grp)
    along_x = face[0] == "y"
    lo, hi = (x0, x1) if along_x else (y0, y1)
    wdt = (hi - lo) / n
    t = 0.06
    for i in range(n):
        a, b = lo + i * wdt + 0.04, lo + (i + 1) * wdt - 0.04
        zs = [(zb + 0.04, z1 - 0.04)]
        if drawers and base:
            zs = [(zb + 0.04, z1 - 0.62), (z1 - 0.55, z1 - 0.04)]
        for (c, e) in zs:
            if along_x:
                yy = y0 - t if face == "y-" else y1
                B.box(mat, a, yy, c, b, yy + t, e, grp=grp)
                B.box(mat, a + 0.22, yy - 0.012 if face == "y-" else yy + t, c + 0.22, b - 0.22, (yy if face == "y-" else yy + t + 0.012), e - 0.22, grp=grp) if e - c > 0.8 else None
                if pulls:
                    ky = yy - 0.05 if face == "y-" else yy + t
                    B.box("brass", (a + b) / 2 - 0.04 if e - c < 0.8 else b - 0.14, ky, (c + e) / 2 - 0.04 if e - c < 0.8 else (c + 0.25 if not base else e - 0.33), ((a + b) / 2 + 0.04 if e - c < 0.8 else b - 0.06), ky + 0.05, ((c + e) / 2 + 0.04 if e - c < 0.8 else (c + 0.33 if not base else e - 0.25)), grp=grp, dens=6)
            else:
                xx = x0 - t if face == "x-" else x1
                B.box(mat, xx, a, c, xx + t, b, e, grp=grp)
                B.box(mat, xx - 0.012 if face == "x-" else xx + t, a + 0.22, c + 0.22, (xx if face == "x-" else xx + t + 0.012), b - 0.22, e - 0.22, grp=grp) if e - c > 0.8 else None
                if pulls:
                    kx = xx - 0.05 if face == "x-" else xx + t
                    B.box("brass", kx, (a + b) / 2 - 0.04 if e - c < 0.8 else b - 0.14, (c + e) / 2 - 0.04 if e - c < 0.8 else (c + 0.25 if not base else e - 0.33), kx + 0.05, ((a + b) / 2 + 0.04 if e - c < 0.8 else b - 0.06), ((c + e) / 2 + 0.04 if e - c < 0.8 else (c + 0.33 if not base else e - 0.25)), grp=grp, dens=6)
    if top:
        o = 0.08
        tx0, ty0, tx1, ty1 = x0, y0, x1, y1
        if face == "x-": tx0 -= o
        if face == "x+": tx1 += o
        if face == "y-": ty0 -= o
        if face == "y+": ty1 += o
        B.box(top, tx0, ty0, z1, tx1, ty1, z1 + 0.12, grp=grp)
