"""Furniture and staging, after the listing photographs.

Pieces are simple boxes and lathes; the baked lighting does most of the work.
Positions are read off photographs 2, 12, 18, 21-23, 45-46 and 50-53.
"""
import math
from mathutils import Vector
from hb import UP

F2 = 9.1


def rbox(B, mat, cx, cy, z0, sx, sy, sz, rot=0.0, skip="z-", **kw):
    """Box centred at (cx, cy) with plan size sx by sy, rotated rot radians about z."""
    c, s = math.cos(rot), math.sin(rot)
    ax, ay = Vector((c, s, 0)), Vector((-s, c, 0))
    o = Vector((cx, cy, z0)) - ax * sx / 2 - ay * sy / 2
    B.obox(mat, o, ax * sx, ay * sy, UP * sz, skip=skip, **kw)


def legs(B, mat, cx, cy, sx, sy, z0, z1, t=0.12, rot=0.0, inset=0.1, **kw):
    c, s = math.cos(rot), math.sin(rot)
    for i in (-1, 1):
        for j in (-1, 1):
            lx, ly = i * (sx / 2 - inset), j * (sy / 2 - inset)
            rbox(B, mat, cx + lx * c - ly * s, cy + lx * s + ly * c, z0, t, t, z1 - z0, rot, skip="z-z+", dens=8, **kw)


def table(B, mat, cx, cy, sx, sy, h, z=0.0, th=0.14, rot=0.0, leg=0.14, solid=True, **kw):
    rbox(B, mat, cx, cy, z + h - th, sx, sy, th, rot, skip="", **kw)
    legs(B, mat, cx, cy, sx, sy, z, z + h - th, leg, rot, **kw)
    if solid:
        r = max(sx, sy) / 2 * 0.9
        B.solid_box(cx - sx / 2 if not rot else cx - r, cy - sy / 2 if not rot else cy - r,
                    cx + sx / 2 if not rot else cx + r, cy + sy / 2 if not rot else cy + r, z, z + h)


def sphere(B, mat, cx, cy, cz, r, n=12, **kw):
    prof = [(max(0.001, r * math.sin(math.pi * i / 8)), cz - r * math.cos(math.pi * i / 8)) for i in range(9)]
    B.lathe(mat, (cx, cy), prof, n=n, **kw)


def chair(B, cx, cy, rot, z=0.0, mat="chairwood"):
    """Oak press-back dining chair (faces +y of its own frame before rotation): saddle seat,
    turned legs and stretchers, raked back posts, five spindles and a deep shaped crest rail."""
    c, s = math.cos(rot), math.sin(rot)
    P = lambda dx, dy, dz=0.0: (cx + dx * c - dy * s, cy + dx * s + dy * c, z + dz)
    cushion(B, mat, P(0, 0.03, 1.47), (0.74 * c, 0.74 * s, 0), (-0.7 * s, 0.7 * c, 0), (0, 0, 0.075), e=0.55, n=8)
    for dx, dy in ((-0.6, 0.55), (0.6, 0.55), (-0.55, -0.55), (0.55, -0.55)):                # legs, splayed a little
        B.tube(mat, P(dx * 1.06, dy * 1.06, 0.0), P(dx * 0.92, dy * 0.92, 1.42), 0.06, n=7)
    for (a0, a1) in (((-0.6, 0.55), (0.6, 0.55)), ((-0.57, 0.5), (-0.57, -0.52)), ((0.57, 0.5), (0.57, -0.52))):
        B.tube(mat, P(a0[0], a0[1], 0.5), P(a1[0], a1[1], 0.5), 0.035, n=6)                 # stretchers
    for dx in (-0.6, 0.6):                                                                 # back posts, raked
        B.tube(mat, P(dx, -0.6, 1.45), P(dx * 1.03, -0.82, 3.05), 0.055, n=7)
    for dx in (-0.36, -0.18, 0.0, 0.18, 0.36):                                             # spindles
        B.tube(mat, P(dx, -0.62, 1.5), P(dx, -0.8, 2.72), 0.028, n=6)
    cushion(B, mat, P(0, -0.84, 3.02), (0.72 * c, 0.72 * s, 0), (-0.045 * s, 0.045 * c, 0), (0, 0, 0.33), e=0.6, n=8)   # crest rail
    B.solid_box(cx - 0.6, cy - 0.6, cx + 0.6, cy + 0.6, z, z + 3)


def fan(B, x, y, zc, drop=1.0, light=True, blade="walnut", grp=None):
    B.tube("iron", (x, y, zc), (x, y, zc - drop), 0.05, grp=grp)
    B.lathe("iron", (x, y), [(0.0, zc - drop), (0.42, zc - drop - 0.05), (0.42, zc - drop - 0.45), (0.2, zc - drop - 0.6)], n=14, grp=grp)
    for i in range(5):
        a = i * 2 * math.pi / 5 + 0.3
        rbox(B, blade, x + 1.45 * math.cos(a), y + 1.45 * math.sin(a), zc - drop - 0.3, 2.1, 0.45, 0.03, a, skip="", grp=grp)
    if light:
        for k in range(4):                               # four frosted shades
            sphere(B, "lampglow", x + 0.3 * math.cos(k * math.pi / 2 + 0.4), y + 0.3 * math.sin(k * math.pi / 2 + 0.4), zc - drop - 0.85, 0.17, n=8, grp="fx")
        B.lights.append((x, y, zc - drop - 1.3, 1.6))


def cushion(B, mat, c, ax, ay, az, e=0.4, n=12, grp=None, dens=None):
    """Soft rounded block (a superellipsoid): centre c and three half-axis vectors.
    e near 1 is an ellipsoid, small e a pillowy box."""
    from hb import Surf
    c, ax, ay, az = Vector(c), Vector(ax), Vector(ay), Vector(az)
    f = lambda v: math.copysign(abs(v) ** e, v)
    s = Surf()
    s.mat, s.grp, s.dens = mat, grp or B.grp, dens or B.dens * 0.6
    s.verts, s.tris, s.uv0, s.lm, s.nrm = [], [], [], [], []
    W_, H_ = 2 * (ax.length + ay.length), 2 * az.length + ax.length
    t = B.mats.get(mat, {}).get("tile", 2.0)
    m = 2 * n
    for j in range(n + 1):
        ph = -math.pi / 2 + math.pi * j / n
        for i in range(m + 1):
            th = 2 * math.pi * i / m
            p = ax * (f(math.cos(ph)) * f(math.cos(th))) + ay * (f(math.cos(ph)) * f(math.sin(th))) + az * f(math.sin(ph))
            s.verts.append(c + p)
            nn = (ax.normalized() * (p.dot(ax) / ax.length_squared) + ay.normalized() * (p.dot(ay) / ay.length_squared)
                  + az.normalized() * (p.dot(az) / az.length_squared))
            s.nrm.append(nn.normalized() if nn.length > 1e-9 else az.normalized())
            s.lm.append((W_ * i / m, H_ * j / n))
            # planar mapping across the two long axes, so a printed fabric lies flat on top
            s.uv0.append((p.dot(ax) / ax.length / t, p.dot(ay) / ay.length / t))
    for j in range(n):
        for i in range(m):
            a = j * (m + 1) + i
            s.tris += [(a, a + 1, a + m + 2), (a, a + m + 2, a + m + 1)]
    s.w, s.h = W_, H_
    B.surfs.append(s)


def sofa(B, x0, y0, x1, y1, back, mat="sofa", z=0.0, seat=1.3, top=2.5, arm=None, cushions=3, grp=None):
    """Low, deep lounge sofa: a plinth and back block with soft seat and back cushions.
    back names the side the backrest is on ('x-','x+','y-','y+')."""
    d = 0.75
    B.box(mat, x0, y0, z + 0.12, x1, y1, z + seat - 0.45, grp=grp)
    bx0, by0, bx1, by1 = x0, y0, x1, y1
    if back == "x+": bx0 = x1 - d
    if back == "x-": bx1 = x0 + d
    if back == "y+": by0 = y1 - d
    if back == "y-": by1 = y0 + d
    B.box(mat, bx0, by0, z + 0.12, bx1, by1, z + top - 0.35, grp=grp)
    along_y = back[0] == "x"
    lo, hi = (y0, y1) if along_y else (x0, x1)
    n = cushions
    sgn = 1 if back[1] == "+" else -1
    for i in range(n):
        a, b = lo + (hi - lo) * i / n, lo + (hi - lo) * (i + 1) / n
        mid, half = (a + b) / 2, (b - a) / 2 - 0.02
        if along_y:
            s0, s1 = (x0, x1 - d) if back == "x+" else (x0 + d, x1)
            cushion(B, mat, ((s0 + s1) / 2, mid, z + seat - 0.12), ((s1 - s0) / 2, 0, 0), (0, half, 0), (0, 0, 0.3), e=0.28, grp=grp)
            bx = (x1 - d) if back == "x+" else (x0 + d)
            cushion(B, mat, (bx - sgn * 0.42, mid, z + seat + 0.75), (0.36, 0, -sgn * 0.08), (0, half - 0.05, 0), (sgn * 0.1, 0, 0.66), e=0.36, grp=grp)
        else:
            s0, s1 = (y0, y1 - d) if back == "y+" else (y0 + d, y1)
            cushion(B, mat, (mid, (s0 + s1) / 2, z + seat - 0.12), (half, 0, 0), (0, (s1 - s0) / 2, 0), (0, 0, 0.3), e=0.28, grp=grp)
            by = (y1 - d) if back == "y+" else (y0 + d)
            cushion(B, mat, (mid, by - sgn * 0.42, z + seat + 0.75), (half - 0.05, 0, 0), (0, 0.36, -sgn * 0.08), (0, sgn * 0.1, 0.66), e=0.36, grp=grp)
    B.solid_box(x0, y0, x1, y1, z, z + 3)


def throw_pillow(B, x, y, z, lean, mat="pillow", size=0.72, grp=None):
    """Square throw pillow leaning back along the unit plan vector lean."""
    lx, ly = lean
    cushion(B, mat, (x, y, z + size * 0.92), (-ly * size, lx * size, 0), (lx * 0.2, ly * 0.2, 0.07), (lx * 0.3, ly * 0.3, size * 0.95), e=0.55, n=8, grp=grp)


def mums(B, x, y, z, r=0.62):
    """Potted chrysanthemums: white pot, a mound of foliage, many small rust blooms."""
    import random
    rnd = random.Random(7)
    B.lathe("porcelain", (x, y), [(0.3, z), (0.42, z + 0.55), (0.38, z + 0.55), (0.0, z + 0.5)], n=14)
    cushion(B, "leaf", (x, y, z + 0.5 + r * 0.42), (r, 0, 0), (0, r, 0), (0, 0, r * 0.75), e=1.0, n=10)
    for _ in range(70):
        a, el = rnd.uniform(0, 2 * math.pi), rnd.uniform(0.05, 1.45)
        d = Vector((math.cos(a) * math.cos(el), math.sin(a) * math.cos(el), math.sin(el) * 0.75))
        c = Vector((x, y, z + 0.5 + r * 0.42)) + d * r * 1.02
        u = d.cross(Vector((0, 0, 1))) if abs(d.z) < 0.95 else Vector((1, 0, 0))
        u.normalize()
        v = d.cross(u)
        k = rnd.uniform(0.07, 0.11)
        cushion(B, "mum", c, u * k, v * k, d.normalized() * 0.05, e=1.0, n=4, dens=4)


def bed(B, x0, y0, x1, y1, head, z=0.0, grp=None, headboard="linen"):
    """Low black platform bed, headboard on side head ('x+' or 'x-'): damask duvet, a quilt
    folded across the foot, two shams and two dark pillows (listing photographs 18 and 37)."""
    sgn = -1 if head == "x+" else 1                      # direction from head to foot
    hx, fx = (x1, x0) if head == "x+" else (x0, x1)
    L, Wd, ym = abs(x1 - x0), (y1 - y0), (y0 + y1) / 2
    B.box("black", x0 - 0.08, y0 - 0.08, z + 0.42, x1 + 0.08, y1 + 0.08, z + 0.85, grp=grp)
    for lx in (x0 + 0.2, x1 - 0.2):
        for ly in (y0 + 0.2, y1 - 0.2):
            B.box("black", lx - 0.08, ly - 0.08, z, lx + 0.08, ly + 0.08, z + 0.42, skip="z+z-", grp=grp, dens=6)
    B.box("linen", x0 + 0.05, y0 + 0.05, z + 0.85, x1 - 0.05, y1 - 0.05, z + 1.75, skip="z-", grp=grp)
    cx = hx + sgn * (L * 0.56)
    cushion(B, "bedding", (cx, ym, z + 1.72), (L * 0.46, 0, 0), (0, Wd / 2 + 0.15, 0), (0, 0, 0.2), e=0.25, grp=grp)
    cushion(B, "bedding", (cx, ym, z + 1.3), (L * 0.46, 0, 0), (0, Wd / 2 + 0.17, 0), (0, 0, 0.55), e=0.2, grp=grp)     # drop down the sides
    cushion(B, "quilt", (fx - sgn * L * 0.2, ym, z + 1.8), (L * 0.2, 0, 0), (0, Wd / 2 + 0.2, 0), (0, 0, 0.2), e=0.3, grp=grp)
    cushion(B, "quilt", (fx - sgn * L * 0.2, ym, z + 1.4), (L * 0.2, 0, 0), (0, Wd / 2 + 0.22, 0), (0, 0, 0.5), e=0.2, grp=grp)
    if headboard:
        B.box(headboard, min(hx, hx + sgn * 0.28), y0 - 0.15, z + 0.5, max(hx, hx + sgn * 0.28), y1 + 0.15, z + 3.9, grp=grp)
    for k in (-1, 1):
        py = ym + k * Wd * 0.25
        cushion(B, "bedding", (hx + sgn * 0.75, py, z + 2.35), (0.28, 0, 0.12 * sgn), (0, Wd * 0.22, 0), (-0.2 * sgn, 0, 0.55), e=0.5, n=8, grp=grp)
        cushion(B, "charcoal", (hx + sgn * 1.35, py * 0.5 + ym * 0.5 + k * 0.55, z + 2.2), (0.22, 0, 0.1 * sgn), (0, Wd * 0.17, 0), (-0.15 * sgn, 0, 0.42), e=0.5, n=8, grp=grp)
    B.solid_box(x0, y0, x1, y1, z, z + 3)


def lamp(B, x, y, z, grp=None):
    B.lathe("porcelain", (x, y), [(0.22, z), (0.28, z + 0.3), (0.08, z + 0.7)], n=10, grp=grp)
    B.lathe("lampglow", (x, y), [(0.38, z + 0.7), (0.3, z + 1.3)], n=12, grp="fx")
    B.lights.append((x, y, z + 1.0, 0.5))


def plant(B, x, y, z, r=0.45, h=1.6, pot="porcelain", grp=None):
    B.lathe(pot, (x, y), [(r * 0.6, z), (r * 0.8, z + r * 1.1), (r * 0.7, z + r * 1.1), (0.0, z + r * 1.0)], n=12, grp=grp)
    for i in range(7):
        a = i * 0.9
        tip = Vector((x + math.cos(a) * r * (0.6 + 0.2 * (i % 3)), y + math.sin(a) * r * (0.6 + 0.2 * (i % 3)), z + h * (0.7 + 0.1 * (i % 4))))
        base = Vector((x + math.cos(a) * 0.1, y + math.sin(a) * 0.1, z + r))
        side = Vector((-math.sin(a), math.cos(a), 0)) * 0.12
        B.poly("plant", [base - side, base + side, tip], grp=grp)


def adirondack(B, cx, cy, rot, z):
    c, s = math.cos(rot), math.sin(rot)
    P = lambda dx, dy: (cx + dx * c - dy * s, cy + dx * s + dy * c)
    m = "adirondack"
    rbox(B, m, cx, cy, z + 0.9, 1.9, 1.7, 0.12, rot, skip="", grp="ex")
    legs(B, m, cx, cy, 2.2, 1.8, z, z + 1.9, 0.14, rot, grp="ex")
    x, y = P(0, -0.95)
    ax, ay = Vector((c, s, 0)), Vector((-s, c, 0))
    o = Vector((x, y, z + 0.9)) - ax * 0.9 - ay * 0.06
    B.obox(m, o, ax * 1.8, ay * 0.12, (UP * 3.0 - ay * 1.0), grp="ex")
    for dx in (-1.1, 1.1):
        x, y = P(dx, 0.0)
        rbox(B, m, x, y, z + 1.9, 0.45, 2.2, 0.1, rot, skip="", grp="ex")
    B.solid_box(cx - 1.0, cy - 1.0, cx + 1.0, cy + 1.0, z, z + 3)


def furnish(B):
    from house import art, can_light, EAVE, D
    B.grp = "in"
    # ---------------- great room ----------------
    # Positions here are measured: floor points picked in listing photograph 4fb1f0b7
    # (camera in the north-east corner) and cast onto the floor. Y() converts them to drawing space.
    from house import yinv as Y
    sofa(B, 7.4, Y(3.5), 16.8, Y(6.8), "y-", cushions=3)             # north run, faces south
    sofa(B, 13.5, Y(6.8), 16.8, Y(13.8), "x+", cushions=3)           # west run, faces the hearth
    B.box("sofa", 15.95, Y(3.5), 0.25, 16.8, Y(6.8), 2.55)           # back carried round the corner
    for (x, y, lean) in ((15.55, 8.3, (1, 0)), (15.6, 12.5, (1, 0)), (9.4, 4.55, (0, -1)), (13.0, 4.5, (0, -1)), (15.3, 5.0, (0.7, -0.7))):
        throw_pillow(B, x, Y(y), 1.45, lean)
    cushion(B, "throw", (14.2, Y(12.9), 1.62), (0.75, 0, 0), (0, 0.6, 0), (0, 0, 0.08), e=0.7, n=8)      # folded throw
    # live-edge coffee table on hairpin legs
    cx_, cy_ = 10.2, Y(10.4)
    cushion(B, "walnut", (cx_, cy_, 1.33), (2.35, 0.12, 0), (-0.06, 1.3, 0), (0, 0, 0.085), e=0.75, n=10)      # live-edge slab
    legs(B, "iron", cx_, cy_, 4.2, 2.2, 0, 1.25, 0.04)
    B.lathe("oak", (cx_, cy_), [(0.9, 1.41), (0.95, 1.46), (0.0, 1.46)], n=18)
    B.lathe("oak", (cx_, cy_), [(0.25, 1.46), (0.55, 1.78), (0.5, 1.78), (0.22, 1.5)], n=16)
    B.solid_box(cx_ - 2.3, cy_ - 1.3, cx_ + 2.3, cy_ + 1.3, 0, 1.5)
    table(B, "darkwood", 6.4, Y(5.9), 1.4, 1.4, 1.9)                   # side table at the sofa's east arm
    table(B, "darkwood", 19.3, Y(9.2), 1.2, 5.0, 2.6, th=0.2)         # console against the stair wall
    plant(B, 19.3, Y(7.2), 2.6, r=0.3, h=1.4)
    # dining: oval oak table and six chairs
    tc = (5.9, Y(22.4))
    ring = [(tc[0] + 3.4 * math.cos(a), tc[1] + 1.75 * math.sin(a)) for a in [i * math.pi / 14 for i in range(28)]]
    B.poly("chairwood", [(x, y, 2.5) for x, y in ring])
    for i in range(28):
        a, b = ring[i], ring[(i + 1) % 28]
        B.quad("chairwood", (a[0], a[1], 2.36), (b[0], b[1], 2.36), (b[0], b[1], 2.5), (a[0], a[1], 2.5))
    B.poly("chairwood", [(x, y, 2.36) for x, y in ring[::-1]])
    for dx in (-1.7, 1.7):
        B.lathe("chairwood", (tc[0] + dx, tc[1]), [(0.5, 0.0), (0.18, 0.5), (0.25, 1.8), (0.4, 2.36)], n=10)
    B.solid_box(tc[0] - 3.2, tc[1] - 1.6, tc[0] + 3.2, tc[1] + 1.6, 0, 2.6)
    # chairs tucked in, as staged
    for (dx, dy, r) in ((-1.4, -1.6, 0.0), (1.4, -1.6, 0.0), (-1.4, 1.6, math.pi), (1.4, 1.6, math.pi),
                        (-3.2, 0, -math.pi / 2), (3.2, 0, math.pi / 2)):
        chair(B, tc[0] + dx, tc[1] + dy, r)
    B.lathe("porcelain", tc, [(0.3, 2.5), (0.65, 2.85), (0.6, 2.85), (0.28, 2.56)], n=14)
    for k in range(5):
        sphere(B, "plant", tc[0] + 0.25 * math.cos(k * 1.3), tc[1] + 0.25 * math.sin(k * 1.3), 2.95, 0.17, n=8)
    # wagon-wheel chandelier over the table
    zc_ = EAVE + (D - tc[1]) - 0.05
    zr_ = 8.3
    B.tube("iron", (tc[0], tc[1], zc_), (tc[0], tc[1], zr_ + 1.8), 0.03)
    n = 20
    for i in range(n):
        a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
        B.tube("iron", (tc[0] + 1.7 * math.cos(a0), tc[1] + 1.7 * math.sin(a0), zr_), (tc[0] + 1.7 * math.cos(a1), tc[1] + 1.7 * math.sin(a1), zr_), 0.045, n=6)
    for i in range(12):
        a = 2 * math.pi * i / 12
        x, y = tc[0] + 1.7 * math.cos(a), tc[1] + 1.7 * math.sin(a)
        B.tube("iron", (x, y, zr_), (x, y, zr_ + 0.3), 0.035, n=6)
        sphere(B, "lampglow", x, y, zr_ + 0.42, 0.1, n=8, grp="fx")
        if i % 4 == 0:
            B.tube("iron", (x, y, zr_), (tc[0], tc[1], zr_ + 1.8), 0.015, n=5)
    B.lights.append((tc[0], tc[1], zr_ - 0.6, 3.0))
    fan(B, 6.5, 13.25, EAVE + D / 2 - 0.1, drop=4.5)
    fan(B, 15.0, 13.25, EAVE + D / 2 - 0.1, drop=4.5)
    # mantel pieces and hearth log holder
    B.lathe("darkwood", (1.1, 11.0), [(0.22, 7.18), (0.36, 7.5), (0.2, 7.85), (0.24, 7.9)], n=12)
    B.lathe("terracotta", (1.1, 15.6), [(0.2, 7.18), (0.36, 7.5), (0.3, 7.8)], n=12)
    plant(B, 1.1, 13.2, 7.18, r=0.2, h=1.0)
    # log hoop on the hearth, left of the stove: an iron ring full of split logs (photograph 45)
    hy, hz_, hr = 10.45, 2.25, 1.15
    for xr_ in (1.55, 2.45):
        prev = None
        for k in range(25):
            a_ = 2 * math.pi * k / 24
            cur = (xr_, hy + hr * math.cos(a_), hz_ + hr * math.sin(a_))
            if prev:
                B.tube("iron", prev, cur, 0.035, n=5)
            prev = cur
    for xr_, yy_ in ((1.55, hy - 0.7), (1.55, hy + 0.7), (2.45, hy - 0.7), (2.45, hy + 0.7)):
        B.tube("iron", (xr_, yy_, 1.05), (xr_, yy_, 1.35), 0.03, n=5)
    import random
    rl = random.Random(5)
    for row in range(5):
        zc_ = 1.42 + row * 0.33
        half = math.sqrt(max(0.05, hr * hr - (zc_ - hz_) ** 2)) - 0.2
        n_ = max(1, int(2 * half / 0.34))
        for j in range(n_):
            yy_ = hy - half + 0.17 + j * (2 * half - 0.34) / max(1, n_ - 1) if n_ > 1 else hy
            B.tube("bark", (1.4 + rl.uniform(-0.05, 0.05), yy_, zc_), (2.6 + rl.uniform(-0.05, 0.05), yy_, zc_), 0.155, n=7)
    # wall art
    art(B, "art_leaf", "y-", Y(1.02), 14.4, 16.6, 4.7, 6.1)
    art(B, "art_roots", "y-", Y(1.02), 3.0, 5.7, 3.9, 5.7)                  # Greg Dunn, Maki-e Neurons
    B.quad("art_banjos", (0.55, Y(1.03), 2.9), (1.8, Y(1.03), 2.9), (1.8, Y(1.03), 6.4), (0.55, Y(1.03), 6.4), fit=(0, 0, 1, 1))   # two banjos and a violin, by the corner
    art(B, "art_frame", "x-", 0.5, Y(24.5), Y(26.2), 4.9, 6.5)              # framed piece right of the south slider
    art(B, "art_metal", "x+", 20.08, Y(18.8), Y(21.4), 12.3, 13.9, frame="paint")   # metal wall art above the kitchen
    # kitchen staging
    mums(B, 13.3, 20.9, 3.03)
    rbox(B, "oak", 15.4, 18.5, 3.03, 1.7, 1.15, 0.08, -math.pi / 4, skip="")
    # (the kettle, grinder, brewer and mortar are part of the backsplash photograph patch)
    # floor registers (positions approximate, from the photographs)
    for vx, vy, along_x in ((1.3, Y(19.6), False), (6.9, Y(26.4), True), (13.0, Y(1.6), True)):
        w_, d_ = (1.0, 0.36) if along_x else (0.36, 1.0)
        B.box("darkwood", vx - w_ / 2, vy - d_ / 2, 0.0, vx + w_ / 2, vy + d_ / 2, 0.025, skip="z-")
        for k in range(1, 8):
            if along_x:
                B.box("black", vx - w_ / 2 + k * w_ / 8 - 0.02, vy - d_ / 2 + 0.05, 0.025, vx - w_ / 2 + k * w_ / 8 + 0.02, vy + d_ / 2 - 0.05, 0.03, skip="z-", dens=4)
            else:
                B.box("black", vx - w_ / 2 + 0.05, vy - d_ / 2 + k * d_ / 8 - 0.02, 0.025, vx + w_ / 2 - 0.05, vy - d_ / 2 + k * d_ / 8 + 0.02, 0.03, skip="z-", dens=4)
    # Sonos speakers on stands
    for sx_, sy_, rot_ in ((1.6, Y(2.1), -math.pi / 4), (1.6, Y(25.8), math.pi / 4)):   # the two east corners, angled in
        B.cyl("white", (sx_, sy_), 0.45, 0.0, 0.06, n=14)
        B.tube("white", (sx_, sy_, 0.06), (sx_, sy_, 2.6), 0.05, n=6)
        rbox(B, "black", sx_, sy_, 2.6, 1.0, 0.4, 0.55, rot_, skip="")
    # plants on the plate shelves over the two big windows, and the bench under the front one
    for px_, py_ in ((4.6, Y(26.5)), (6.9, Y(26.5)), (9.3, Y(26.5)), (7.6, Y(1.4)), (11.9, Y(1.4))):
        plant(B, px_, py_, 7.79, r=0.22, h=0.95)
    B.box("walnut", 13.7, Y(1.15), 1.35, 17.0, Y(2.5), 1.55)                 # bench under the leaf panel, behind the sofa
    B.box("walnut", 13.7, Y(1.1), 1.55, 17.0, Y(1.3), 3.0)
    for bx_ in (13.85, 16.65):
        B.box("walnut", bx_, Y(1.15), 0, bx_ + 0.2, Y(2.5), 1.35)
    B.solid_box(13.7, Y(1.1), 17.0, Y(2.5), 0, 3)
    # ---------------- mudroom (photograph 54): slab bench and a coat shelf with scarves, south wall
    my = Y(26.85)
    B.box("cedar", 34.6, my - 1.35, 1.25, 38.4, my, 1.45)
    B.box("cedar", 34.6, my - 0.14, 1.45, 38.4, my, 2.9)
    for bx_ in (34.6, 38.2):
        B.box("cedar", bx_, my - 1.35, 0, bx_ + 0.2, my, 2.2)
    B.box("oak", 34.4, my - 0.85, 5.65, 38.6, my, 5.75)
    B.box("oak", 34.4, my - 0.1, 5.2, 38.6, my, 5.65)
    for k_, m_ in enumerate(("pillow", "quilt", "linen")):
        cushion(B, m_, (35.5 + k_ * 0.8, my - 0.22, 4.35), (0.14, 0, 0), (0, 0.06, 0), (0, 0, 0.95), e=0.35, n=8)      # scarves
    B.solid_box(34.6, my - 1.35, 38.4, my, 0, 3)
    hbx = 24.52
    for k in range(12):
        a_ = k * math.pi / 6
        B.tube("iron", (hbx, Y(24.4), 4.9), (hbx, Y(24.4) + 0.55 * math.cos(a_), 4.9 + 0.55 * math.sin(a_)), 0.02, n=4)
    # ---------------- laundry closet: stacked washer / dryer at the west end, shelves beside
    for z in (0.05, 3.2):
        B.box("white", 28.0, 10.0, z, 30.5, 12.3, z + 3.0)
        ring = [(29.25 + 0.8 * math.cos(a), 12.32, z + 1.5 + 0.8 * math.sin(a)) for a in [i * math.pi / 10 for i in range(20)]]
        B.poly("steel", ring[::-1])
        ring2 = [(29.25 + 0.55 * math.cos(a), 12.33, z + 1.5 + 0.55 * math.sin(a)) for a in [i * math.pi / 10 for i in range(20)]]
        B.poly("tvscreen", ring2[::-1])
    for z in (1.5, 3.2, 4.9, 6.4):
        B.box("white", 24.4, 9.9, z, 27.8, 11.4, z + 0.08)
    # ---------------- primary bedroom, 14'10" x 14'9"
    bed(B, 38.4, 3.9, 45.2, 10.4, "x+")
    for y in (2.5, 11.8):
        table(B, "darkwood", 44.4, y, 1.6, 1.5, 2.0)
        lamp(B, 44.5, y, 2.0)
    B.box("black", 40.6, 12.2, 0, 43.4, 13.65, 4.1)                   # tall dresser, south wall west of the bath door
    B.box("black", 39.6, 0.6, 0, 42.6, 2.1, 2.9)                      # low dresser on the window wall
    B.solid_box(40.6, 12.2, 43.4, 13.65, 0, 4.2)
    B.solid_box(39.6, 0.6, 42.6, 2.1, 0, 3)
    for z in (1.0, 2.0, 3.0):
        B.box("iron", 40.9, 12.17, z, 43.1, 12.2, z + 0.03, skip="y+")
    art(B, "art_blue", "x+", 45.78, Y(6.0), Y(9.0), 4.9, 6.85)        # Greg Dunn, Neurogenesis I
    fan(B, 38.3, 7.1, 8.1, drop=0.5)
    # ---------------- loft (listing photographs 21 and 22) ----------------
    B.grp = "in2"
    g = "in2"
    sofa(B, 28.4, 7.3, 31.7, 14.5, "x-", mat="leather", z=F2, cushions=3, top=2.9, grp=g)          # reclining sofa, faces the TV
    sofa(B, 38.2, Y(6.2), 43.0, Y(9.3), "y-", mat="leather", z=F2, cushions=2, top=2.9, grp=g)      # second recliner, north side
    for (x, y, lean) in ((29.6, 8.4, (-1, 0)), (29.6, 13.4, (-1, 0)), (39.4, 7.3, (0, -1))):
        throw_pillow(B, x, y, F2 + 1.45, lean, mat="linen", size=0.8, grp=g)
    # oak coffee table with a slatted lower shelf
    table(B, "chairwood", 35.2, 10.9, 2.0, 4.0, 1.5, z=F2, grp=g)
    for k in range(6):
        B.box("chairwood", 34.35 + k * 0.3, 9.1, F2 + 0.45, 34.55 + k * 0.3, 12.7, F2 + 0.5, grp=g, dens=6)
    rbox(B, "chairwood", 35.2, 10.6, F2 + 1.5, 1.0, 1.4, 0.12, 0.1, grp=g)                         # tray
    plant(B, 35.2, 10.9, F2 + 1.62, r=0.14, h=0.6, grp=g)
    B.box("walnut", 43.9, 7.0, F2 + 0.3, 45.4, 13.0, F2 + 1.9, grp=g)                    # media console
    B.box("black", 45.15, 6.6, F2 + 2.6, 45.35, 13.4, F2 + 6.3, grp=g)                   # television
    B.quad("tvscreen", (45.14, 6.7, F2 + 2.7), (45.14, 13.3, F2 + 2.7), (45.14, 13.3, F2 + 6.2), (45.14, 6.7, F2 + 6.2), grp=g, flip=True)
    B.solid_box(43.9, 7.0, 45.4, 13.0, F2, F2 + 6)
    # keyboard on an X stand by the south wall
    kx_, ky_ = 34.5, Y(20.2)
    rbox(B, "black", kx_, ky_, F2 + 2.4, 4.3, 0.95, 0.22, 0, skip="", grp=g)
    rbox(B, "white", kx_, ky_ - 0.12, F2 + 2.62, 4.0, 0.5, 0.02, 0, skip="z-", grp=g)
    for sx_ in (-1, 1):
        B.beam("black", (kx_ - 1.3, ky_ + sx_ * 0.3, F2), (kx_ + 1.3, ky_ + sx_ * 0.3, F2 + 2.4), 0.08, 0.08, grp=g)
        B.beam("black", (kx_ + 1.3, ky_ + sx_ * 0.3, F2), (kx_ - 1.3, ky_ + sx_ * 0.3, F2 + 2.4), 0.08, 0.08, grp=g)
    B.solid_box(kx_ - 2.2, ky_ - 0.5, kx_ + 2.2, ky_ + 0.5, F2, F2 + 3)
    fan(B, 34.0, 11.8, 17.1, drop=0.6, grp=g)
    # ---------------- upstairs bedroom (photograph 23) ----------------
    bed(B, 62.7, 9.5, 69.4, 15.9, "x+", z=F2, grp=g, headboard=None)
    table(B, "white", 68.5, 17.4, 1.5, 1.4, 2.0, z=F2, grp=g)
    lamp(B, 68.5, 17.4, F2 + 2.0, grp=g)
    fan(B, 59.0, 12.7, 17.1, drop=0.6, grp=g)
    # short attic-access doors in the north knee wall, either side of the dormer
    ky2 = Y(7.13)
    for x0 in (53.3, 60.3):
        B.quad("oakdoor", (x0 + 1.9, ky2, F2 + 0.3), (x0, ky2, F2 + 0.3), (x0, ky2, F2 + 3.5), (x0 + 1.9, ky2, F2 + 3.5), fit=(0, 0.45, 1, 1), grp=g)
        for bx0_, bx1_, bz0_, bz1_ in ((x0 - 0.28, x0, 0.05, 3.8), (x0 + 1.9, x0 + 2.18, 0.05, 3.8), (x0 - 0.28, x0 + 2.18, 3.5, 3.8)):
            B.box("oak", bx0_, ky2 - 0.01, F2 + bz0_, bx1_, ky2 + 0.05, F2 + bz1_, grp=g)
    # towels
    B.grp = "in"
    for (x, y) in ((39.9, 22.18),):
        B.box("linen", x, y - 0.12, 4.9, x + 1.6, y, 6.3)
    # ---------------- screened porch ----------------
    B.grp = "ex"
    zf = -0.25
    sx0, sx1, sy0, sy1 = 37.0, 43.6, 28.6, 31.6        # hung clear of the outer rail
    B.box("white", sx0, sy0, zf + 1.3, sx1, sy1, zf + 1.55, grp="ex")
    B.box("white", sx0, sy0, zf + 1.55, sx0 + 0.18, sy1, zf + 3.3, grp="ex")
    B.box("white", sx1 - 0.18, sy0, zf + 1.55, sx1, sy1, zf + 3.3, grp="ex")
    B.box("white", sx0, sy0, zf + 1.55, sx1, sy0 + 0.18, zf + 3.3, grp="ex")
    B.box("blueseat", sx0 + 0.2, sy0 + 0.2, zf + 1.55, sx1 - 0.2, sy1 - 0.05, zf + 2.1, skip="z-", grp="ex")
    for k in range(3):
        a = sx0 + 0.3 + k * 2.1
        B.box("blueseat", a, sy0 + 0.2, zf + 2.1, a + 1.9, sy0 + 0.75, zf + 3.5, skip="z-", grp="ex")
    for x in (sx0 + 0.1, sx1 - 0.1):
        for y in (sy0 + 0.1, sy1 - 0.1):
            B.tube("chrome", (x, y, zf + 3.3), (x, y, 8.6), 0.035, n=5, grp="ex")
    B.solid_box(sx0, sy0, sx1, sy1, zf, zf + 3.5)
    table(B, "cedar", 7.0, 31.6, 5.0, 2.6, 2.45, z=zf, grp="ex")
    for (dx, r) in ((-1.4, math.pi), (1.4, math.pi)):
        chair(B, 7.0 + dx, 29.4, r + math.pi, z=zf, mat="cedar")
        chair(B, 7.0 + dx, 33.5, r, z=zf, mat="cedar")
    for (x, r) in ((19.0, math.pi), (22.0, math.pi)):
        chair(B, x, 27.9, r, z=zf, mat="cedar")
    fan(B, 23.0, 30.3, 8.6, drop=0.6, light=False, blade="cedar", grp="ex")
    # ---------------- deck ----------------
    # owner: one pair in the outer north corner facing out, one pair mid-deck facing east
    # with a plant on a metal stand between them
    for (x, y, r) in ((-9.5, 4.8, 3 * math.pi / 4 - 0.3), (-7.2, 2.7, 3 * math.pi / 4 + 0.3),
                      (-8.6, 11.6, math.pi / 2), (-8.6, 16.6, math.pi / 2)):
        adirondack(B, x, y, r, zf)
    legs(B, "iron", -9.0, 14.1, 1.3, 1.3, zf, zf + 1.6, 0.06, grp="ex")
    rbox(B, "iron", -9.0, 14.1, zf + 1.6, 1.3, 1.3, 0.06, 0, skip="", grp="ex")
    plant(B, -9.0, 14.1, zf + 1.66, r=0.5, h=2.0, grp="ex")
    B.solid_box(-9.7, 13.4, -8.3, 14.8, zf, zf + 3)
    kx, ky = -2.2, 3.4                              # at the front end of the side deck, as in the hero photograph
    B.lathe("kamado", (kx, ky), [(0.0, zf + 1.7), (0.7, zf + 1.9), (0.95, zf + 2.6), (0.9, zf + 3.4), (0.5, zf + 4.0), (0.2, zf + 4.15), (0.0, zf + 4.15)], n=16, grp="ex")
    legs(B, "iron", kx, ky, 1.5, 1.5, zf, zf + 2.0, 0.07, grp="ex")
    B.solid_box(kx - 0.9, ky - 0.9, kx + 0.9, ky + 0.9, zf, zf + 4)
    B.grp = "in"
