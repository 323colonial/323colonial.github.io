"""Walls, floors, flat ceilings, doors and windows generated from plan.json.

plan.json (see plan_extract.py) holds the measured floor plans of the listing's 3D
tour: room outlines, wall outlines, door and window openings, in model feet. Every
wall here is a closed slab with a finish on both faces, chosen by the room found on
each side, so rooms close by construction and nothing is typed in by hand except the
rules below (heights, which doors stand open, which finish a room has).
"""
import json, math, os
from hb import Wall, UP
from parts import window, poly_window, door, casing, wbox
import house
from house import H1, F2, CF, EAVE, yinv

PLAN = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "plan.json")))
OUTDOORS = ("Deck", "Screened Porch")                   # plan "rooms" that are not indoors

# Plan correction: the scan boxes the hearth in as a chimney chase standing in the room.
# Indoors it is a stone surround on a flat wall, so the chase is removed and the east
# wall made continuous behind it.
PLAN["rooms"] = [r for r in PLAN["rooms"] if r["name"] != "Fireplace"]
for r in PLAN["rooms"]:
    if r["floor"] == "main" and len(r["poly"]) > 8:
        r["poly"] = [[0.5, y] if (x < 1.9 and 9.5 < y < 17.3) else [x, y] for x, y in r["poly"]]
PLAN["walls"] = [w for w in PLAN["walls"] if not (w["floor"] == "main" and all(-2.9 < x < 1.8 and 9.5 < y < 17.3 for x, y in w["poly"]))]
PLAN["walls"].append({"floor": "main", "poly": [[0.16, 9.9], [0.54, 9.9], [0.54, 16.9], [0.16, 16.9]]})
# The scan missed the mudroom window (listing photograph 54, south wall).
PLAN["windows"].append({"floor": "main", "poly": [[40.3, 26.9], [42.7, 26.9], [42.7, 27.3], [40.3, 27.3]]})
D0 = 26.5                                               # house depth in drawn feet (roof maths)


def in_poly(x, y, poly):
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        (xi, yi), (xj, yj) = poly[i], poly[j]
        if (yi > y) != (yj > y) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
            inside = not inside
        j = i
    return inside


def room_at(floor, x, y):
    """Name of the indoor room at a point, '' for an unnamed one, None for outdoors."""
    for r in PLAN["rooms"]:
        if r["floor"] == floor and in_poly(x, y, r["poly"]):
            return None if r["name"] in OUTDOORS else r["name"]
    return None


def is_open(x, y):
    """No floor above here: the great room, and the entry and stair well beside it."""
    return x < 20.07 or (x < 24.2 and y < 13.3)


def paint(floor, name):
    if name is None:
        return "siding"
    if "Primary Bedroom" in name:
        return "paint_blue"
    if "Bathroom" in name:
        return "paint_salt"
    if floor == "upper" and name == "Bedroom":
        return "paint_sage"
    if name == "Garage":
        return "garage"
    return "paint"


def floor_mat(floor, name):
    if name == "Garage":
        return "concrete"
    if "Bathroom" in name or name == "Laundry":
        return "tile"
    return "oakfloor" if floor == "main" else "carpet"


def roof_in(y):
    """Underside of the roof over the outer walls (measured y)."""
    yd = yinv(y)
    return EAVE + max(0.0, min(yd, D0 - yd))


def upper_ceiling(x, y):
    if 20.2 < x < 29.3 and y > 17.3:                    # the bath's shed dormer keeps full height
        return CF
    return min(CF, roof_in(y))


EPS = 0.012     # each wall is built this much longer at both ends (see Run.pt)


class Run:
    """A plan wall reduced to a centre line: start a, unit direction d, length L, thickness t."""

    def __init__(self, w):
        P = w["poly"]
        best = max(range(len(P)), key=lambda i: math.dist(P[i], P[(i + 1) % len(P)]))
        ex, ey = P[(best + 1) % len(P)][0] - P[best][0], P[(best + 1) % len(P)][1] - P[best][1]
        L = math.hypot(ex, ey)
        dx, dy = ex / L, ey / L
        if abs(dx) > abs(dy):
            if dx < 0: dx, dy = -dx, -dy
        elif dy < 0:
            dx, dy = -dx, -dy
        nx, ny = -dy, dx
        ss = [p[0] * dx + p[1] * dy for p in P]
        oo = [p[0] * nx + p[1] * ny for p in P]
        self.floor, self.d, self.n = w["floor"], (dx, dy), (nx, ny)
        self.s0, self.s1 = min(ss), max(ss)
        self.o = (min(oo) + max(oo)) / 2
        self.t = max(oo) - min(oo)
        self.L = self.s1 - self.s0 + 2 * EPS

    def pt(self, s, off=0.0):
        s -= EPS
        return (self.d[0] * (self.s0 + s) + self.n[0] * (self.o + off), self.d[1] * (self.s0 + s) + self.n[1] * (self.o + off))

    def sides(self):
        """Rooms on the left (+n) and right (-n) of the run, sampled along it."""
        out = []
        for sgn in (1, -1):
            names = [room_at(self.floor, *self.pt(self.L * f, sgn * (self.t / 2 + 0.45))) for f in (0.2, 0.5, 0.8)]
            real = [n for n in names if n is not None]
            out.append(max(set(real), key=real.count) if real else None)
        return out

    def locate(self, poly):
        """(s0, s1) of an opening lying in this wall, else None."""
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        o = cx * self.n[0] + cy * self.n[1]
        ss = [p[0] * self.d[0] + p[1] * self.d[1] - self.s0 + EPS for p in poly]
        if abs(o - self.o) > 0.35 or min(ss) < -0.3 or max(ss) > self.L + 0.3 or max(ss) - min(ss) < 1.2:
            return None
        return max(0.05, min(ss)), min(self.L - 0.05, max(ss))


def profile(run, fn, lift, lo):
    """Top edge of a wall as (s, z) samples of a ceiling function along the run."""
    n = max(1, int(run.L / 0.5))
    pts = []
    for i in range(n + 1):
        s = run.L * i / n
        pts.append((s, max(lo, fn(*run.pt(s)) + lift)))
    return pts


def skip(run, left, right):
    x, y = run.pt(run.L / 2)
    along_y = abs(run.d[1]) > 0.7
    if left is None and right is None:
        return True                                     # porch rails, the chimney box, the deck edge
    if run.floor == "main":
        # the stair's open side is a stringer and balustrade (house.stairs), not a wall
        if along_y and 19.8 < x < 20.7 and 4.3 < y < 13.4:
            return True
        # nor are the lines the plan draws across the stair (its foot, and between the two flights)
        return (not along_y) and 19.9 < x < 24.3 and 4.0 < y < 13.0
    if {left, right} <= {None, "Open To Below"}:
        return True                                     # the void over the great room
    if along_y and (x < 1.0 or x > 69.2):
        return True                                     # gable ends: the house wall carries on up
    if not along_y and y > 26.6:
        return True                                     # likewise the bath dormer's south wall
    if x < 24.4 and y < 17.3:
        return True                                     # loft edge and stair well: guard rails
    knee = 5.0 if x < 45.7 else 6.9
    return y < knee - 0.5                               # dormer alcoves are built with the roof


def door_rule(run, s0, s1, left, right, exterior):
    """How an opening is filled: dict(kind=..., ...)."""
    w = s1 - s0
    x, y = run.pt((s0 + s1) / 2)
    names = [n or "" for n in (left, right)]
    closet = any(k in n for n in names for k in ("Closet", "Pantry", "Stairs", "Garage")) or "Primary" in names
    if exterior:
        if w > 7:
            return dict(kind="garage")
        if w > 5:
            return dict(kind="slider", open_lo=y > 13)
        if y < 2 and 20 < x < 25:
            return dict(kind="slab", angle=95, mats=("frontdoor_in", "frontdoor_out"), trim="extrim")
        if y > 26:
            return dict(kind="slab", angle=100, out=True, mats=("halfglass_in", "halfglass_out"), trim="green")
        return dict(kind="slab", angle=0, mats=("white", "white"), trim="extrim")
    if w > 4.4:
        return dict(kind="open") if "Laundry" in names else dict(kind="pair")
    if "Garage" in names:
        return dict(kind="slab", angle=0, mats=("white", "white"))      # the garage door off the mudroom is painted white
    return dict(kind="slab", angle=0 if closet else 86, mats=("oakdoor", "oakdoor"))


def window_rule(run, s0, s1, inside_room):
    w = s1 - s0
    name = inside_room or ""
    if run.floor == "upper":
        return F2 + 2.3, F2 + 6.5
    if name == "Garage":
        return 2.6, 6.4
    if w < 3.3:
        x, _ = run.pt((s0 + s1) / 2)
        return (3.65, 6.5) if 14 < x < 22 else (3.3, 6.3)   # over the kitchen sink / small bath windows
    return 2.3, 6.8


def build(B):
    runs = [Run(w) for w in PLAN["walls"]]
    built = []          # (run, Wall, level, inside sign) for opening placement
    for run in runs:
        left, right = run.sides()
        if run.L < 0.3 or skip(run, left, right):
            continue
        a, b = run.pt(0), run.pt(run.L)
        if run.floor == "upper":
            g = "in2"
            w = Wall(B, a, b, F2, CF, run.t, paint("upper", left) if left is not None else "paint",
                     paint("upper", right) if right is not None else "paint", grp=g,
                     top=profile(run, upper_ceiling, 0.25, F2 + 0.5))
            built.append((run, w, "upper", 1 if left is not None else -1, left, right))
            continue
        exterior = left is None or right is None
        if not exterior:
            oL, oR = is_open(*run.pt(run.L / 2, 1.0)), is_open(*run.pt(run.L / 2, -1.0))
            top = None
            z1 = H1 if not (oL or oR) else F2
            if oL and oR:
                z1, top = CF, profile(run, lambda x, y: roof_in(y), 0.3, H1)
            w = Wall(B, a, b, 0, z1, run.t, paint("main", left), paint("main", right), top=top, grp="in")
            built.append((run, w, "main", 1, left, right))
            continue
        ins = 1 if left is not None else -1
        room = left if ins > 0 else right
        garage = room == "Garage"
        mi = paint("main", room)
        mats = (mi, "siding") if ins > 0 else ("siding", mi)
        grps = ("ex" if garage else "in", "ex") if ins > 0 else ("ex", "ex" if garage else "in")
        w = Wall(B, a, b, -0.5, H1, run.t, mats[0], mats[1], grp=grps[0], grpR=grps[1])
        built.append((run, w, "main", ins, left, right))
        # the same wall carried up to the roof (gable ends, and the strip under the eaves)
        def top_fn(x, y):
            return F2 - 0.3 if (20.2 < x < 29.3 and y > 26) else roof_in(y)
        prof = profile(run, top_fn, 0.3, H1)
        if max(z for _, z in prof) > H1 + 0.2:
            px, py = run.pt(run.L / 2, ins * 1.2)
            up = room_at("upper", px, py)
            mu = "paint" if (up is None or is_open(px, py)) else paint("upper", up)
            gi = "in" if is_open(px, py) else "in2"
            mats = (mu, "siding") if ins > 0 else ("siding", mu)
            grps = (gi, "ex") if ins > 0 else ("ex", gi)
            wu = Wall(B, a, b, H1, CF, run.t, mats[0], mats[1], grp=grps[0], grpR=grps[1], top=prof, solid=False)
            built.append((run, wu, "top", ins, left, right))

    def host(o, levels):
        for run, w, level, ins, left, right in built:
            if level in levels and (run.floor == o["floor"] or level == "top"):
                span = run.locate(o["poly"])
                if span:
                    return run, w, level, ins, left, right, span
        return None

    # ---- doors
    for o in PLAN["doors"]:
        h = host(o, ("main",) if o["floor"] == "main" else ("upper",))
        if not h:
            continue
        run, w, level, ins, left, right, (s0, s1) = h
        z0 = F2 if level == "upper" else 0.0
        left = room_at(run.floor, *run.pt((s0 + s1) / 2, run.t / 2 + 0.6))
        right = room_at(run.floor, *run.pt((s0 + s1) / 2, -(run.t / 2 + 0.6)))
        exterior = level == "main" and (left is None or right is None)
        rule = door_rule(run, s0, s1, left, right, exterior)
        gin = "in2" if level == "upper" else "in"
        k = rule["kind"]
        if k == "slider":
            house.slider(B, w, s0, s1, 6.8, open_lo=rule["open_lo"]) if ins > 0 else slider_flipped(B, w, s0, s1, rule["open_lo"])
        elif k == "garage":
            w.hole(s0, s1, -0.5, 6.4)
            off = -ins * (run.t / 2 - 0.05)
            B.quad("garagedoor", w.pt(s0, -0.5, off), w.pt(s1, -0.5, off), w.pt(s1, 6.4, off), w.pt(s0, 6.4, off),
                   grp="ex", fit=(0, 0, 1, 1), flip=ins > 0)
            B.quad("garage", w.pt(s0, -0.5, off + ins * 0.05), w.pt(s1, -0.5, off + ins * 0.05), w.pt(s1, 6.4, off + ins * 0.05),
                   w.pt(s0, 6.4, off + ins * 0.05), grp="ex", flip=ins < 0)
            casing(B, w, s0, s1, -0.5, 6.4, -ins, mat="extrim", sill=False, grp="ex")
            p, q = w.pt(s0, 0), w.pt(s1, 0)
            B.solid(p.x, p.y, q.x, q.y, -1, 7)
        elif k == "open":
            w.hole(s0, s1, z0, z0 + 6.75)
            for side in (1, -1):
                casing(B, w, s0, s1, z0, z0 + 6.75, side, sill=False, grp=gin)
            # bifold doors folded back at each jamb, standing out into the hall (listing photograph 20)
            out_ = -1 if "Laundry" in (left or "") else 1
            for sj, step in ((s0 + 0.03, 1), (s1 - 0.03, -1)):
                for k_ in range(2):
                    sa = sj + step * k_ * 0.16
                    o_ = w.pt(sa + (0.11 if out_ < 0 else 0), z0 + 0.05, out_ * run.t / 2)
                    B.obox("oakdoor", o_, w.d * (0.11 * out_), w.n * (1.25 * out_), UP * 6.65, grp=gin, fit=(0, 0, 1, 1))
                p_, q_ = w.pt(sj, 0, out_ * run.t / 2), w.pt(sj, 0, out_ * (run.t / 2 + 1.25))
                B.solid(p_.x, p_.y, q_.x, q_.y, z0, z0 + 7)
        elif k == "pair":
            # a closed pair of closet doors, faced toward the room they open from
            names = [left or "", right or ""]
            front = -1 if ("Closet" in names[0] or names[0] == "Primary") else 1
            w.hole(s0, s1, z0, z0 + 6.75)
            for side, m in ((front, "oakdoors2"), (-front, "oak")):
                off = side * 0.06
                B.quad(m, w.pt(s0, z0, off), w.pt(s1, z0, off), w.pt(s1, z0 + 6.75, off), w.pt(s0, z0 + 6.75, off),
                       grp=gin, fit=(0, 0, 1, 1) if m == "oakdoors2" else None, flip=side > 0)
                casing(B, w, s0, s1, z0, z0 + 6.75, side, sill=False, grp=gin)
            p, q = w.pt(s0, 0), w.pt(s1, 0)
            B.solid(p.x, p.y, q.x, q.y, z0, z0 + 7)
        else:
            # swing into the more private room (or outward for the porch door)
            if exterior:
                swing = -ins if rule.get("out") else ins
                mat, back = rule["mats"] if ins > 0 else rule["mats"][::-1]
                door(B, w, s0, s1, 6.8, swing=swing, hinge="lo", angle=rule["angle"], mat=mat, mat_back=back,
                     case=(ins,), grp="in" if ins > 0 else "ex", grp_back="ex" if ins > 0 else "in")
                casing(B, w, s0, s1, 0, 6.8, -ins, mat=rule["trim"], sill=False, grp="ex")
            else:
                hallish = lambda n: n is None or n == "" or any(k_ in n for k_ in ("Living", "Loft", "Stairs"))
                swing = 1 if (hallish(right) and not hallish(left)) else -1
                door(B, w, s0, s1, z0 + 6.75, z0=z0, swing=swing, hinge="lo", angle=rule["angle"], mat=rule["mats"][0], grp=gin)

    # ---- windows
    for o in PLAN["windows"]:
        if o["floor"] == "upper":
            cx = sum(p[0] for p in o["poly"]) / len(o["poly"])
            if 30 < cx < 62:
                continue                                # dormer windows are built with the dormers
        h = host(o, ("main",) if o["floor"] == "main" else ("upper", "top"))
        if not h:
            continue
        run, w, level, ins, left, right, (s0, s1) = h
        room = left if ins > 0 else right
        z0, z1 = window_rule(run, s0, s1, room)
        if level == "top":                              # an upstairs window in a wall carried up from below
            z0, z1, room = F2 + 2.3, F2 + 6.5, None
        units = max(1, int(round((s1 - s0) / 2.9)))
        x, _ = run.pt((s0 + s1) / 2)
        gin = "ex" if room == "Garage" else ("in2" if level != "main" else "in")
        window(B, w, s0, s1, z0, z1, units=units, inside=ins, grp_in=gin,
               shelf=7.7 if (level == "main" and s1 - s0 > 5 and x < 20) else None)

    # ---- the great room's tall gable glazing, above the sliders (from the photographs)
    for run, w, level, ins, left, right in built:
        x, y = run.pt(run.L / 2)
        if level != "top" or x > 1.0 or abs(run.d[1]) < 0.7:
            continue
        lo, hi = run.pt(0)[1], run.pt(run.L)[1]
        zo = EAVE + 2.4
        for (ya, yb, rise_south) in ((4.1, 10.0, False), (17.4, 23.3, True)):
            if lo - 0.1 <= ya and yb <= hi + 0.1:
                sa, sb = ya - lo, yb - lo
                za, zb = (zo + (sb - sa), zo) if not rise_south else (zo, zo + (sb - sa))
                # taller toward the ridge
                mid = (lo + hi) / 2
                if not rise_south:
                    pts = [(sa, 8.7), (sb, 8.7), (sb, zo + (sb - sa)), (sa, zo)]
                else:
                    pts = [(sa, 8.7), (sb, 8.7), (sb, zo), (sa, zo + (sb - sa))]
                poly_window(B, w, pts, inside=ins, grp_in="in")

    # The tall wall over the entry closet (note 106): the plan's upper floor stops at the loft's
    # knee wall, so nothing closed the attic's east end above the closet door. In the
    # photographs that wall runs straight up to the roof, with the return-air grille in it.
    ya, yb = 0.62, 5.12
    prof = [(i * (yb - ya) / 8, roof_in(ya + i * (yb - ya) / 8) + 0.3) for i in range(9)]
    Wall(B, (24.29, ya), (24.29, yb), F2 - 0.02, CF, 0.38, "paint", "paint", top=prof, grp="in", grpR="in2", solid=False).build()
    B.box("white", 24.06, 2.3, 9.9, 24.1, 4.1, 11.3, grp="in")          # return-air grille
    for k in range(1, 9):
        B.box("paint", 24.04, 2.4, 9.9 + k * 0.155, 24.06, 4.0, 9.9 + k * 0.155 + 0.05, grp="in", dens=4)
    # oak baseboard along every painted wall face, broken at the door openings
    for run, w, level, ins, left, right in built:
        if level == "top":
            continue
        for side, mat, grp in ((1, w.mL, w.grpL), (-1, w.mR, w.grpR)):
            if not (mat or "").startswith("paint"):
                continue
            cuts = sorted(rng for _, passable, rng in w.holes if passable)
            s_ = 0.0
            for c0, c1 in cuts + [(w.L, w.L)]:
                if c0 - 0.3 - s_ > 0.25:
                    wbox(B, w, "oak", s_, c0 - (0.3 if c0 < w.L else 0), w.z0, w.z0 + 0.42, side * w.t / 2, side * (w.t / 2 + 0.045), grp=grp)
                s_ = c1 + 0.3
    for _, w, *_ in built:
        w.build()

    floors_and_ceilings(B)


def slider_flipped(B, w, s0, s1, open_lo):
    """house.slider assumes the interior is on the wall's left; mirror the wall for the other case."""
    house.slider(B, w, s0, s1, 6.8, open_lo=open_lo)


def floors_and_ceilings(B):
    for r in PLAN["rooms"]:
        name, poly, fl = r["name"], r["poly"], r["floor"]
        if name in OUTDOORS:
            continue
        area = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
        if area < 0:
            poly = poly[::-1]
        if fl == "main":
            g = "ex" if name == "Garage" else "in"
            B.poly(floor_mat(fl, name), [(x, y, 0.0) for x, y in poly], grp=g, dens=28 if len(poly) > 8 else None, uvrot=True)
            B.floor(poly, 0.0)
        elif name not in ("Open To Below", "Stairs"):
            B.poly(floor_mat(fl, name), [(x, y, F2) for x, y in poly], grp="in2")
            B.floor(poly, F2)
    # Room outlines stop at the wall faces, so the strips under walls, in doorways and beside
    # the open stair would have no floor. A slab just below the finished floors closes them.
    B.quad("oakfloor", (0.2, 0.3, -0.03), (46.0, 0.3, -0.03), (46.0, 27.2, -0.03), (0.2, 27.2, -0.03), grp="in", dens=6, uvrot=True)
    B.quad("concrete", (46.0, 0.3, -0.03), (70.0, 0.3, -0.03), (70.0, 27.2, -0.03), (46.0, 27.2, -0.03), grp="ex", dens=4)
    for x0, y0, x1, y1 in ((24.3, 0.4, 69.9, 27.1), (20.07, 13.35, 24.3, 27.1)):
        B.quad("carpet", (x0, y0, F2 - 0.03), (x1, y0, F2 - 0.03), (x1, y1, F2 - 0.03), (x0, y1, F2 - 0.03), grp="in2", dens=6)
    # the same slabs are walkable, so a doorway threshold never drops the player through (note 100)
    B.floor([(0.2, 0.3), (70.0, 0.3), (70.0, 27.2), (0.2, 27.2)], 0.0)
    B.floor([(24.3, 0.4), (69.9, 0.4), (69.9, 27.1), (24.3, 27.1)], F2)
    B.floor([(20.07, 13.35), (24.3, 13.35), (24.3, 27.1), (20.07, 27.1)], F2)
    # ...and the visible strips get a proper finished floor: every doorway, and the footprint
    # of every plan wall that is not built (the open side of the stair, the loft edge).
    def strip(poly, floor):
        cx = sum(p[0] for p in poly) / len(poly)
        cy = sum(p[1] for p in poly) / len(poly)
        if floor == "upper" and is_open(cx, cy):
            return
        near = [room_at(floor, cx + dx, cy + dy) for dx, dy in ((0.7, 0), (-0.7, 0), (0, 0.7), (0, -0.7))]
        names = [n for n in near if n is not None]
        if not names:
            return
        mat = "tile" if all("Bathroom" in n for n in names) else floor_mat(floor, [n for n in names if "Bathroom" not in n][0])
        a = sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))
        pts = poly if a > 0 else poly[::-1]
        z = (F2 if floor == "upper" else 0.0) - 0.004
        B.poly(mat, [(x, y, z) for x, y in pts], grp="in2" if floor == "upper" else "in", uvrot=floor == "main")
    for o in PLAN["doors"]:
        strip(o["poly"], o["floor"])
    for w in PLAN["walls"]:
        run = Run(w)
        left, right = run.sides()
        if run.L >= 0.3 and (left is not None or right is not None) and skip(run, left, right):
            strip(w["poly"], w["floor"])
    # tiled mudroom and back hall inside the main room's outline
    B.quad("tile", (29.72, 22.75, 0.02), (46.0, 22.75, 0.02), (46.0, 27.2, 0.02), (29.72, 27.2, 0.02), grp="in")      # runs under the walls, so no sliver of oak shows at its edges
    # flat ceiling (the underside of the upper floor) wherever there is a room below and no void above
    main = [r for r in PLAN["rooms"] if r["floor"] == "main" and r["name"] not in OUTDOORS]
    xs = sorted({round(p[0], 2) for r in PLAN["rooms"] for p in r["poly"]} | {20.07, 24.2})
    ys = sorted({round(p[1], 2) for r in PLAN["rooms"] for p in r["poly"]} | {13.3})
    spans = {}                                      # (x0, x1) -> list of [y0, y1], merged down the rows
    for j in range(len(ys) - 1):
        y0, y1 = ys[j], ys[j + 1]
        if y1 - y0 < 0.02:
            continue
        start = None
        for i in range(len(xs) - 1):
            x0, x1 = xs[i], xs[i + 1]
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            covered = x1 - x0 >= 0.02 and not is_open(cx, cy) and any(in_poly(cx, cy, r["poly"]) for r in main)
            if covered and start is None:
                start = x0
            if start is not None and (not covered or i == len(xs) - 2):
                end = x1 if covered else x0
                rows = spans.setdefault((start, end), [])
                if rows and abs(rows[-1][1] - y0) < 0.03:
                    rows[-1][1] = y1                    # same span as the row above: one bigger panel, no seam
                else:
                    rows.append([y0, y1])
                start = None
    for (start, end), rows in spans.items():
        for y0, y1 in rows:
            B.quad("ceiling", (start, y1, H1), (end, y1, H1), (end, y0, H1), (start, y0, H1),
                   grp="ex" if start > 46 else "in", dens=14)
