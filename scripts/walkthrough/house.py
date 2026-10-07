"""323 Colonial Dr: the house as geometry.

Room positions and sizes come from the measured floor plans of the listing's
3D tour (owner-supplied screenshots, 6 Oct 2026); heights, windows and finishes
come from the listing photographs. Sheets A-4 / A-5 were the first, rougher source. Units are feet; see hb.py for the frame
(X = west, Y = south, Z = up, origin at the north-east exterior corner at
main-floor level).
"""
import math
from mathutils import Vector
from hb import Builder, Wall, UP
from parts import wbox, casing, glazing, window, poly_window, door, rail, cabinet_run

W, D, GW = 46.0, 26.5, 70.0      # house width, depth, west end of garage
H1, F2, CF = 8.1, 9.1, 17.1      # main ceiling, loft floor, flat upper ceiling
RIDGE = D / 2
EAVE = 9.7                        # interior ceiling height at the outside wall face
GPK = EAVE + RIDGE                # great-room cathedral runs to the ridge
SX0, SX1, SY0, SY1 = 20.07, 24.1, 4.45, 12.77   # SX0 = east face of the wall above the kitchen (plan)   # stair well (x east/west, y bottom/top)
SWX = 24.1                        # stair west wall, also the kitchen / closet line
BX = 30.9                         # primary bedroom east wall
KNL, KNB, KS = 4.93, 6.77, 20.9     # upper knee walls (drawn y): loft north, bedroom north, south
NR = 14                           # risers
GROUND_N = -1.6                   # grade at the front wall
BASE = -9.6                       # walkout basement slab

MATS = {
    # name: tex (basename in textures/), tile (ft per repeat), color (linear tint), rough, metal
    "paint":      dict(color=(0.905, 0.885, 0.84), rough=0.9),   # SW Greek Villa, matched to the photographs
    "ceiling":    dict(color=(0.905, 0.89, 0.855), rough=0.95),
    "paint_blue": dict(color=(0.21, 0.30, 0.46), rough=0.85),  # SW Debonair, matched to how the photographs render it
    "paint_salt": dict(color=(0.610, 0.644, 0.591), rough=0.6),   # SW Sea Salt
    "paint_sage": dict(color=(0.638, 0.571, 0.480), rough=0.9),   # SW Accessible Beige (upstairs bedroom)
    "oakfloor":   dict(tex="oakfloor", tile=12.0, color=(1.0, 1.0, 1.0), rough=0.3),   # generated strip oak (oakfloor.py)
    "oak":        dict(tex="oak_veneer_01", tile=3.0, color=(1.0, 0.86, 0.66), rough=0.5),
    "trim":       dict(tex="oak_veneer_01", tile=3.0, color=(1.0, 0.86, 0.66), rough=0.5),
    "oakdoor":    dict(tex="oakdoor", fit=True, rough=0.5),
    "oakdoors2":  dict(tex="oakdoors2", fit=True, rough=0.5),
    "carpet":     dict(tex="carpet", tile=3.0, color=(1, 1, 1), rough=1.0),
    "tile":       dict(tex="floortile", tile=4.0, rough=0.35),
    "bath_wainscot": dict(tex="bath_wainscot", fit=True, wrap=True, rough=0.4),
    "bath_shelf": dict(tex="bath_shelf", fit=True, rough=0.6), "bath_cabinet": dict(tex="bath_cabinet", fit=True, rough=0.6),
    "walltile":   dict(tex="interior_tiles", tile=3.0, color=(0.95, 0.9, 0.82), rough=0.4),
    "granite":    dict(tex="granite", tile=2.5, rough=0.15),
    "stone":      dict(tex="rustic_stone_wall", tile=7.0, color=(0.95, 0.9, 0.78), rough=0.9),
    "fpstone":    dict(tex="rustic_stone_wall", fit=True, color=(1.0, 0.86, 0.66), rough=0.9),   # plain stone: the photo crop had the stove and log rack in it
    "hearth":     dict(tex="rustic_stone_wall", tile=5.0, color=(0.75, 0.68, 0.6), rough=0.8),
    "siding":     dict(tex="weathered_plank_siding", tile=5.0, color=(1.0, 0.42, 0.26), rough=0.7),
    "cedar":      dict(tex="wood_floor_deck", tile=7.0, color=(1.0, 0.7, 0.5), rough=0.55),
    "extrim":     dict(color=(0.30, 0.11, 0.07), rough=0.7),
    "roof":       dict(tex="roof_slates_02", tile=6.0, color=(0.3, 0.3, 0.36), rough=0.9),
    "deck":       dict(tex="wood_floor_deck", tile=7.0, color=(0.6, 0.27, 0.2), rough=0.6, rot=45),   # solid dark mahogany stain; boards laid on the diagonal (owner)
    "deckstain":  dict(color=(0.33, 0.12, 0.08), rough=0.7),
    "lattice":    dict(tex="lattice", tile=0.75, rough=0.8, alpha=True),
    "grass":      dict(tex="leafy_grass", tile=9.0, rough=1.0),
    "leaves":     dict(tex="forest_leaves_02", tile=12.0, color=(0.62, 0.58, 0.5), rough=1.0),
    "gravel":     dict(tex="gravel_floor", tile=7.0, color=(0.8, 0.8, 0.8), rough=1.0),
    "pavers":     dict(tex="gravel_floor", tile=5.0, color=(0.75, 0.62, 0.55), rough=1.0),
    "concrete":   dict(color=(0.62, 0.61, 0.58), rough=0.9),
    "parge":      dict(color=(0.8, 0.8, 0.78), rough=0.9),
    "bark":       dict(tex="bark_brown_02", tile=4.0, rough=1.0),
    "winframe":   dict(color=(0.09, 0.085, 0.075), rough=0.5),
    "white":      dict(color=(0.9, 0.9, 0.88), rough=0.5),
    "porcelain":  dict(color=(0.93, 0.93, 0.92), rough=0.12),
    "steel":      dict(tex="brushed", tile=1.0, color=(0.78, 0.78, 0.77), rough=0.34, metal=1.0),
    "chrome":     dict(color=(0.6, 0.58, 0.54), rough=0.3, metal=1.0),
    "brass":      dict(color=(0.75, 0.6, 0.3), rough=0.3, metal=1.0),
    "brassrail":  dict(color=(0.62, 0.45, 0.16), rough=0.45),
    "black":      dict(color=(0.02, 0.02, 0.02), rough=0.5),
    "iron":       dict(color=(0.03, 0.028, 0.025), rough=0.6),
    "green":      dict(color=(0.112, 0.122, 0.100), rough=0.5),   # SW Pewter Green
    "frontdoor_in":  dict(tex="frontdoor_in", fit=True, rough=0.5),
    "frontdoor_out": dict(tex="frontdoor_out", fit=True, rough=0.5),
    "halfglass_in":  dict(tex="halfglass_in", fit=True, rough=0.5),
    "halfglass_out": dict(tex="halfglass_out", fit=True, rough=0.5),
    "garagedoor": dict(tex="garagedoor", fit=True, color=(1.7, 1.7, 1.7), rough=0.6),   # lifted: the doors face north and sit in shade
    "garage":     dict(color=(0.75, 0.75, 0.73), rough=0.9),
    "glass":      dict(color=(0.6, 0.7, 0.7), rough=0.05, glass=True),
    "mirror":     dict(color=(0.9, 0.9, 0.9), rough=0.02, metal=1.0),
    "kit_s_base":  dict(tex="kit_s_base", fit=True, rough=0.5),
    "kit_s_upper": dict(tex="kit_s_upper", fit=True, rough=0.5),
    "kit_s_splash": dict(tex="kit_s_splash", fit=True, rough=0.4),
    "kit_fridge":  dict(tex="kit_fridge", fit=True, rough=0.3),
    "kit_range":   dict(tex="kit_range", fit=True, rough=0.3),
    "kit_w_upper": dict(tex="kit_w_upper", fit=True, rough=0.5),
    "kit_w_fridgetop": dict(tex="kit_w_fridgetop", fit=True, rough=0.5),
    "kit_w_base":  dict(tex="kit_w_base", fit=True, rough=0.5),
    "isl_a": dict(tex="isl_a", fit=True, rough=0.5), "isl_b": dict(tex="isl_b", fit=True, rough=0.5),
    "isl_c": dict(tex="isl_c", fit=True, rough=0.5), "isl_d": dict(tex="isl_d", fit=True, rough=0.5),
    "art_banjos": dict(tex="art_banjos", fit=True, rough=0.6),
    "art_metal":  dict(tex="art_metal", fit=True, rough=0.5),
    "art_frame":  dict(tex="art_frame", fit=True, rough=0.5),
    "art_bird":   dict(tex="art_bird", fit=True, rough=0.6),
    "art_roots":  dict(tex="art_roots", fit=True, rough=0.4),
    "art_leaf":   dict(tex="art_leaf", fit=True, rough=0.6),
    "fire":       dict(tex="fire", fit=True, emit=3.0),
    "mum":        dict(color=(0.72, 0.27, 0.06), rough=0.9),
    "leaf":       dict(color=(0.1, 0.22, 0.07), rough=0.8),
    "throw":      dict(tex="fabric", tile=1.5, color=(0.35, 0.23, 0.17), rough=1.0),
    "sofa":       dict(tex="fabric", tile=2.0, color=(0.80, 0.78, 0.73), rough=1.0),
    "pillow":     dict(tex="fabric", tile=1.5, color=(0.62, 0.27, 0.17), rough=1.0),
    "leather":    dict(color=(0.20, 0.12, 0.08), rough=0.55),
    "walnut":     dict(tex="oak_veneer_01", tile=3.0, color=(0.34, 0.17, 0.09), rough=0.4),
    "darkwood":   dict(tex="oak_veneer_01", tile=3.0, color=(0.12, 0.09, 0.08), rough=0.5),
    "chairwood":  dict(tex="oak_veneer_01", tile=3.0, color=(0.85, 0.55, 0.32), rough=0.45),   # red oak
    "bedding":    dict(tex="bedding", tile=3.2, rough=1.0),
    "quilt":      dict(tex="fabric", tile=1.5, color=(0.3, 0.42, 0.52), rough=1.0),
    "charcoal":   dict(tex="fabric", tile=1.0, color=(0.09, 0.09, 0.1), rough=1.0),
    "art_blue":   dict(tex="art_blue", fit=True, rough=0.4),
    "linen":      dict(tex="fabric", tile=2.0, color=(0.92, 0.91, 0.88), rough=1.0),
    "blueseat":   dict(tex="fabric", tile=2.0, color=(0.08, 0.14, 0.42), rough=1.0),
    "tubshell":   dict(color=(0.45, 0.44, 0.42), rough=0.5),
    "water":      dict(color=(0.35, 0.8, 0.8), rough=0.05, emit=0.25),
    "screen":     dict(color=(0.05, 0.05, 0.05), rough=1.0, screen=True),
    "tvscreen":   dict(color=(0.01, 0.01, 0.012), rough=0.08),
    "lampglow":   dict(color=(1.0, 0.85, 0.6), emit=6.0),
    "plant":      dict(color=(0.12, 0.3, 0.1), rough=0.8),
    "terracotta": dict(color=(0.55, 0.25, 0.15), rough=0.8),
    "adirondack": dict(color=(0.88, 0.88, 0.85), rough=0.7),
    "canopy":     dict(tex="canopy", fit=True, alpha=True, rough=1.0, unlit=0.75),
    "kamado":     dict(color=(0.55, 0.06, 0.03), rough=0.3),
}


def zc(y):
    """Interior ceiling height under the 12:12 roof."""
    return min(CF, EAVE + min(y, D - y))


def zg(y):
    """Great-room cathedral ceiling."""
    return min(GPK, EAVE + min(y, D - y))


def zr(y):
    """Top of roof."""
    return (EAVE + 1.0) + min(y, D - y)


def build():
    B = Builder()
    B.mats = MATS
    # Fixtures, stair, roof, porch, deck and furniture are still drawn by hand, in the
    # original "drawn" feet, and are stretched once onto the measured plan by calibrate().
    legacy_main(B)
    stairs(B)
    legacy_upper(B)
    roof(B)
    exterior(B)
    porch_and_deck(B)
    site(B)
    import furnish
    furnish.furnish(B)
    calibrate(B)
    # Walls, floors, flat ceilings, doors and windows are generated from plan.json,
    # in measured feet. New work belongs in this space.
    import planshell
    planshell.build(B)
    return B


# Depth calibration against the vector floor plan published with the listing's
# 3D tour (zillowstatic floor_map, in metres). The layout above was read off a
# screenshot of that plan and sits within a few inches in x, but the house is
# 27.4 ft deep outside, not 26.5, and interior walls land 0.5 to 0.9 ft further
# south than drawn here. Rather than restate every literal, the finished model
# is stretched in y through these (drawn, measured) pairs.
Y_CAL = [(0.0, 0.0), (26.5, 27.4)]
# One straight scale, deliberately: a piecewise stretch bends every sloped plane it
# crosses (the cathedral ceiling no longer met the wall above the loft, leaving a dark
# slot at the ridge). Hand-drawn pieces that must land on a measured line are placed with
# yinv() instead.


def ycal(y):
    if y <= Y_CAL[0][0]:
        return y
    for (a, fa), (b, fb) in zip(Y_CAL, Y_CAL[1:]):
        if y <= b:
            return fa + (fb - fa) * (y - a) / (b - a)
    return y + Y_CAL[-1][1] - Y_CAL[-1][0]


def yinv(y):
    """Measured y -> the y to draw at, so a piece placed from the photographs lands where it was measured."""
    if y <= Y_CAL[0][1]:
        return y
    for (a, fa), (b, fb) in zip(Y_CAL, Y_CAL[1:]):
        if y <= fb:
            return a + (b - a) * (y - fa) / (fb - fa)
    return y - (Y_CAL[-1][1] - Y_CAL[-1][0])


def calibrate(B):
    for sf in B.surfs:
        sf.verts0 = [v.copy() for v in sf.verts]      # as drawn; project.py maps texels through these
        for v in sf.verts:
            v.y = ycal(v.y)
    B.solids = [(a, ycal(b), c, ycal(d), e, f) for a, b, c, d, e, f in B.solids]
    for fl in B.floors:
        fl["poly"] = [[x, ycal(y)] for x, y in fl["poly"]]
        if "ramp" in fl:
            y0, z0, y1, z1 = fl["ramp"]
            fl["ramp"] = [ycal(y0), z0, ycal(y1), z1]
    B.lights = [(x, ycal(y), z, p) for x, y, z, p in B.lights]
    for d in B.doors:
        d["hinge"] = (d["hinge"][0], ycal(d["hinge"][1]))
        x0, y0, x1, y1 = d["seg"]
        d["seg"] = (x0, ycal(y0), x1, ycal(y1))


def flat(B, mat, x0, y0, x1, y1, z, up=True, **kw):
    B.quad(mat, (x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z), flip=not up, **kw)


def slope(B, mat, x0, x1, y0, y1, zf, holes=(), up=False, **kw):
    """Planar strip z = zf(y) between y0 and y1; holes as (hx0, hx1, hy0, hy1)."""
    pts = [(x0, y0, zf(y0)), (x1, y0, zf(y0)), (x1, y1, zf(y1)), (x0, y1, zf(y1))]
    hs = [[(a, c, zf(c)), (b, c, zf(c)), (b, e, zf(e)), (a, e, zf(e))] for a, b, c, e in holes]
    B.poly(mat, pts, holes=hs, flip=not up, **kw)


DORMERS = [(7.4, 10.6), (34.2, 37.9), (55.8, 59.6)]   # north dormers, interior x range
DORMER_Y = [1.4, 1.4, 3.0]        # how far each dormer's face sits back up the roof from the front wall (plan, hero photograph)
ZD = 16.3                                              # dormer ceiling
YD = ZD - EAVE                                          # where it meets the slope


# ----------------------------------------------------------------------------------



def slider(B, w, s0, s1, z1, open_lo=False):
    """Two-panel sliding glass door with grids; one panel slid open for passage."""
    w.hole(s0, s1, 0, z1)
    casing(B, w, s0, s1, 0, z1, 1, sill=False)
    casing(B, w, s0, s1, 0, z1, -1, mat="extrim", sill=False, grp="ex")
    mid = (s0 + s1) / 2
    fixed = (s0, mid) if not open_lo else (mid, s1)
    glazing(B, w, fixed[0], fixed[1], 0.05, z1, grid=(3, 5), fw=0.2)
    # the sliding panel parked over the fixed one, just outboard
    p = Wall(B, w.pt(fixed[0] + 0.25, 0, -0.14).to_2d(), w.pt(fixed[1] + 0.25, 0, -0.14).to_2d(), 0, z1, 0.1)
    glazing(B, p, 0, p.L, 0.05, z1, grid=(3, 5), fw=0.2)
    wbox(B, w, "winframe", s0, s1, 0, 0.05, -0.2, 0.2, grp="ex")
    a, b = w.pt(fixed[0], 0), w.pt(fixed[1], 0)
    B.solid(a.x, a.y, b.x, b.y, 0, z1)


# ----------------------------------------------------------------------------------
def legacy_main(B):
    B.grp = "in"
    # loft edge fascia over the kitchen
    B.box("oak", SX0, SY1, H1 - 0.05, SX0 + 0.38, 16.86, F2 + 0.05)
    B.box("paint", SX0, 16.86, H1 - 0.05, SX0 + 0.38, D - 0.5, F2 + 0.05)
    kitchen(B)
    fireplace(B)
    baths_main(B)
    for x, y, z, p in ((27.5, 5.0, 7.6, 0.8), (22.2, 2.0, 8.5, 1.0), (27.5, 11.2, 7.0, 0.5)):
        B.lights.append((x, y, z, p))
    for x, y in ((27.5, 14.5), (30.5, 18.0), (31.5, 24.3), (38.0, 24.3), (43.5, 24.3)):
        can_light(B, x, y, H1)


def kitchen(B):
    """Cabinet runs as plain boxes whose fronts carry squared-up patches of the listing
    photographs (prepare.sh). Positions along the south wall were solved from photograph 48,
    along the west wall from the tour's fixture data; y is in drawn feet."""
    kx = SWX                            # face of the west wall
    yb, yu, yw = 24.0, 24.95, 25.985    # base fronts, upper fronts, wall face

    def south(mat, y, xa, xb, za, zb, x0, x1, z0, z1):
        """Front-facing quad showing the part of a patch that covers x0..x1, z0..z1."""
        B.quad(mat, (xa, y, za), (xb, y, za), (xb, y, zb), (xa, y, zb),
               fit=((xa - x0) / (x1 - x0), (za - z0) / (z1 - z0), (xb - x0) / (x1 - x0), (zb - z0) / (z1 - z0)))

    def west(mat, x, ya, yb_, za, zb, u0=0.0, u1=1.0):
        """East-facing quad from ya (south end) to yb_ (north end)."""
        B.quad(mat, (x, ya, za), (x, yb_, za), (x, yb_, zb), (x, ya, zb), fit=(u0, 0, u1, 1))

    # ---- south run
    B.box("oak", 12.7, yb, 0.3, kx, 26.0, 2.9, skip="z+")
    B.box("black", 12.7, yb + 0.2, 0, kx, 26.0, 0.3, skip="z+z-")
    south("kit_s_base", yb - 0.015, 12.7, 21.85, 0.08, 2.68, 12.7, 21.85, 0.08, 2.68)
    # granite top in four pieces around an undermount double-bowl sink
    sx0, sx1, sy0, sy1 = 17.0, 19.4, 24.35, 25.55
    for x0_, y0_, x1_, y1_ in ((12.6, yb - 0.08, sx0, 26.0), (sx1, yb - 0.08, kx, 26.0), (sx0, yb - 0.08, sx1, sy0), (sx0, sy1, sx1, 26.0)):
        B.box("granite", x0_, y0_, 2.9, x1_, y1_, 3.02)
    for bx0_, bx1_ in ((sx0, 18.15), (18.25, sx1)):
        z0_, z1_ = 2.3, 2.92
        B.quad("steel", (bx0_, sy0, z0_), (bx1_, sy0, z0_), (bx1_, sy1, z0_), (bx0_, sy1, z0_))
        B.quad("steel", (bx0_, sy0, z0_), (bx0_, sy0, z1_), (bx1_, sy0, z1_), (bx1_, sy0, z0_))
        B.quad("steel", (bx1_, sy1, z0_), (bx1_, sy1, z1_), (bx0_, sy1, z1_), (bx0_, sy1, z0_))
        B.quad("steel", (bx0_, sy1, z0_), (bx0_, sy1, z1_), (bx0_, sy0, z1_), (bx0_, sy0, z0_))
        B.quad("steel", (bx1_, sy0, z0_), (bx1_, sy0, z1_), (bx1_, sy1, z1_), (bx1_, sy1, z0_))
        B.cyl("chrome", ((bx0_ + bx1_) / 2, (sy0 + sy1) / 2), 0.12, z0_, z0_ + 0.015, n=10)       # drain
    B.box("steel", 18.15, sy0, 2.3, 18.25, sy1, 2.9)
    # pull-down gooseneck faucet with a side lever
    fx_, fy_ = 18.2, 25.78
    B.cyl("chrome", (fx_, fy_), 0.09, 3.02, 3.2, n=12)
    B.tube("chrome", (fx_, fy_, 3.2), (fx_, fy_, 4.05), 0.045)
    prev = (fx_, fy_, 4.05)
    for k in range(1, 8):
        a_ = math.pi * k / 7
        cur = (fx_, fy_ - 0.32 + 0.32 * math.cos(a_), 4.05 + 0.32 * math.sin(a_))
        B.tube("chrome", prev, cur, 0.045)
        prev = cur
    B.tube("chrome", prev, (fx_, fy_ - 0.64, 3.72), 0.055)
    B.tube("chrome", (fx_ + 0.09, fy_, 3.3), (fx_ + 0.3, fy_ - 0.05, 3.42), 0.025)
    for xa, xb, zb in ((12.93, 16.45, 4.42), (16.45, 19.85, 3.5), (19.85, kx, 4.42)):    # tile, lower under the window
        south("kit_s_splash", yw, xa, xb, 3.03, zb, 12.93, 24.1, 3.03, 4.58)
    for xa, xb in ((12.76, 16.35), (19.87, 21.76)):
        B.box("oak", xa, yu, 4.42, xb, 26.0, 6.93)
        south("kit_s_upper", yu - 0.015, xa, xb, 4.42, 6.93, 12.76, 21.76, 4.42, 6.93)
    # the valance board across the window, with an LED bar hidden behind it (owner)
    B.box("oak", 16.35, yu, 6.41, 19.87, yu + 0.1, 6.93)
    south("kit_s_upper", yu - 0.015, 16.35, 19.87, 6.41, 6.93, 12.76, 21.76, 4.42, 6.93)
    B.box("lampglow", 16.7, 25.12, 6.72, 19.5, 25.2, 6.78, grp="fx")      # tucked up behind the board
    B.lights.append((18.1, 25.35, 5.9, 0.35))
    prism(B, "oak", [(21.76, 26.0), (21.76, yu), (23.1, 23.75), (kx, 23.75), (kx, 26.0)], 4.42, 6.93, caps=True)   # diagonal corner upper
    # ---- west run: range, a short counter, refrigerator
    ry0, ry1 = 21.07, 23.98                              # 36 in. dual-fuel range
    B.box("steel", 21.75, ry0, 0.2, kx, ry1, 3.0)
    B.box("black", 21.85, ry0 + 0.05, 3.0, kx - 0.1, ry1 - 0.05, 3.06)
    west("kit_range", 21.735, ry1, ry0, 0.2, 3.0)
    B.box("oak", 23.1, 20.3, 4.42, kx, 23.75, 6.93)       # uppers; the microwave is part of the patch
    west("kit_w_upper", 23.085, 23.75, 20.3, 4.42, 6.93, u0=0.10)
    B.box("oak", 22.0, 19.85, 0.3, kx, ry0, 2.9)
    B.box("black", 22.2, 19.85, 0, kx, ry0, 0.3, skip="z+z-")
    B.box("granite", 21.92, 19.85, 2.9, kx, ry0, 3.02)
    west("kit_w_base", 21.985, ry0, 19.85, 0.3, 2.75)
    for ya_ in (24.0, 21.93):
        B.quad("kit_s_splash", (kx - 0.02, ya_, 3.03), (kx - 0.02, ya_ - 2.07, 3.03), (kx - 0.02, ya_ - 2.07, 4.42), (kx - 0.02, ya_, 4.42),
               fit=(0.655, 0.0, 0.84, 0.897))
    # door on the diagonal corner cabinet (the same door as its neighbour)
    B.quad("kit_s_upper", (21.75, yu - 0.012, 4.42), (23.09, 23.738, 4.42), (23.09, 23.738, 6.93), (21.75, yu - 0.012, 6.93), fit=(0.79, 0, 1, 1))
    fy0, fy1 = 16.85, 19.85
    B.box("steel", 21.3, fy0, 0.1, kx, fy1, 5.83)         # refrigerator
    # French doors over a freezer drawer: seams and bar handles (LG, stainless)
    fm = (fy0 + fy1) / 2
    B.box("black", 21.285, fy0, 2.4, 21.3, fy1, 2.45, skip="x+")
    B.box("black", 21.285, fm - 0.012, 2.45, 21.3, fm + 0.012, 5.83, skip="x+")
    for y_ in (fm - 0.13, fm + 0.13):
        B.tube("steel", (21.16, y_, 2.95), (21.16, y_, 5.3), 0.035)
        for z_ in (3.05, 5.2):
            B.tube("steel", (21.16, y_, z_), (21.3, y_, z_), 0.02, n=6)
    B.tube("steel", (21.16, fy0 + 0.35, 2.15), (21.16, fy1 - 0.35, 2.15), 0.035)
    for y_ in (fy0 + 0.45, fy1 - 0.45):
        B.tube("steel", (21.16, y_, 2.15), (21.3, y_, 2.15), 0.02, n=6)
    B.box("oak", 22.0, fy0, 5.85, kx, fy1, 6.93)
    west("kit_w_fridgetop", 21.985, fy1, fy0, 5.85, 6.93)
    B.box("oak", 21.6, fy0 - 0.12, 0, kx, fy0, 6.93)
    B.solid_box(12.7, yb - 0.1, kx, 26.0, 0, 7)
    B.solid_box(21.3, fy0 - 0.12, kx, 24.0, 0, 7)
    # island: outline from the tour's fixture data (a boomerang, seating on the outer two sides);
    # its kitchen-side faces carry patches from photograph 35
    top = [(18.48, 19.52), (18.48, 16.56), (15.2, 16.56), (12.27, 19.49), (12.27, 22.23), (15.47, 22.23), (15.47, 20.81), (16.76, 19.52)]
    base = [(18.4, 19.44), (18.4, 16.9), (15.35, 16.9), (12.6, 19.63), (12.6, 22.15), (15.39, 22.15), (15.39, 20.78), (16.73, 19.44)]
    prism(B, "oak", base, 0.0, 2.9)
    prism(B, "granite", top, 2.9, 3.03, caps=True)
    for i in range(len(top)):
        a, b = top[i], top[(i + 1) % len(top)]
        B.solid(a[0], a[1], b[0], b[1], 0, 3.1)
    e = 0.012
    B.quad("isl_a", (18.4 + e, 16.9, 0.0), (18.4 + e, 19.44, 0.0), (18.4 + e, 19.44, 2.9), (18.4 + e, 16.9, 2.9), fit=(0, 0, 1, 1))
    B.quad("isl_b", (18.4, 19.44 + e, 0.0), (16.73, 19.44 + e, 0.0), (16.73, 19.44 + e, 2.9), (18.4, 19.44 + e, 2.9), fit=(0, 0, 1, 1))
    B.quad("isl_c", (16.73 + e, 19.44 + e, 0.0), (15.39 + e, 20.78 + e, 0.0), (15.39 + e, 20.78 + e, 2.9), (16.73 + e, 19.44 + e, 2.9), fit=(0, 0, 1, 1))
    B.quad("isl_d", (15.39 + e, 20.78, 0.0), (15.39 + e, 22.15, 0.0), (15.39 + e, 22.15, 2.9), (15.39 + e, 20.78, 2.9), fit=(0, 0, 1, 1))
    # brass foot rail hugging the base on the seating side, on short brackets, a finial at each end
    bar = [(18.3, 16.62), (15.23, 16.62), (12.32, 19.52), (12.32, 22.1)]
    for a, b in zip(bar, bar[1:]):
        B.tube("brassrail", (a[0], a[1], 0.62), (b[0], b[1], 0.62), 0.06, n=8)
    for ex_, ey_ in (bar[0], bar[-1]):
        B.lathe("brassrail", (ex_, ey_), [(0.0, 0.5), (0.1, 0.54), (0.13, 0.62), (0.1, 0.7), (0.0, 0.74)], n=10)
    for (x, y), (ix, iy) in zip(bar + [(16.8, 16.62), (13.75, 18.1)], [(18.3, 16.9), (15.35, 16.9), (12.6, 19.63), (12.6, 22.1), (16.8, 16.9), (13.95, 18.3)]):
        B.tube("brassrail", (x, y, 0.62), (ix, iy, 0.62), 0.035, n=6)
    for x, y in ((20.7, 19.5), (20.7, 22.8)):       # two recessed lights, in a row in front of the range and fridge (video)
        can_light(B, x, y, H1)


def prism(B, mat, poly, z0, z1, caps=False, **kw):
    """Vertical prism from a CCW (seen from above) plan polygon."""
    n = len(poly)
    area = sum(poly[i][0] * poly[(i + 1) % n][1] - poly[(i + 1) % n][0] * poly[i][1] for i in range(n))
    if area < 0:
        poly = poly[::-1]
    for i in range(n):
        a, b = poly[i], poly[(i + 1) % n]
        B.quad(mat, (a[0], a[1], z0), (b[0], b[1], z0), (b[0], b[1], z1), (a[0], a[1], z1), **kw)
    if caps:
        B.poly(mat, [(x, y, z1) for x, y in poly], **kw)
        B.poly(mat, [(x, y, z0) for x, y in poly[::-1]], **kw)


def can_light(B, x, y, z, r=0.25, grp=None):
    B.poly("lampglow", [(x + r * math.cos(a), y + r * math.sin(a), z - 0.01) for a in [i * math.pi / 6 for i in range(12)]],
           flip=True, grp="fx")
    B.lights.append((x, y, z - 1.1, 1.0))          # below the ceiling, so it does not burn a hot spot into it


def fireplace(B):
    # stone surround proud of the east wall, between the two sliders
    y0, y1, zt = 9.45, 17.05, 6.9
    B.quad("fpstone", (0.95, y1, 1.05), (0.95, y0, 1.05), (0.95, y0, zt), (0.95, y1, zt), fit=(0, 0, 1, 1), dens=30, flip=True)
    B.box("hearth", 0.5, y0, 0, 0.95, y1, zt, skip="x+x-z-")
    B.box("hearth", 0.5, y0 - 0.15, 0, 2.9, y1 + 0.15, 1.05, skip="x-z-")
    # wood-stove insert: a flat black surround on the stone, the firebox standing out of it,
    # a framed glass door with the fire behind, and a louvred blower grille below
    B.box("black", 0.95, 11.2, 1.05, 1.03, 15.3, 4.3, skip="x-")                       # surround panel
    B.box("iron", 1.03, 11.7, 1.12, 1.62, 14.8, 3.95, skip="x-")                       # firebox
    B.box("black", 1.62, 11.85, 1.75, 1.68, 14.65, 3.8, skip="x-")                     # door frame
    B.quad("fire", (1.685, 14.45, 1.95), (1.685, 12.05, 1.95), (1.685, 12.05, 3.6), (1.685, 14.45, 3.6), fit=(0, 0, 1, 1), grp="fx", flip=True)
    B.tube("chrome", (1.72, 14.56, 2.4), (1.72, 14.56, 3.1), 0.03, n=6)               # door handle
    for k in range(5):                                                                 # blower louvres
        B.box("black", 1.62, 11.9, 1.2 + k * 0.1, 1.66, 14.6, 1.25 + k * 0.1, skip="x-", dens=6)
    B.box("iron", 1.0, 11.6, 3.95, 1.75, 14.9, 4.02)                                    # top lip
    # mantel
    B.box("oak", 0.5, y0 - 0.25, zt, 1.75, y1 + 0.25, zt + 0.28)
    B.box("oak", 0.5, y0 - 0.1, zt - 0.3, 1.2, y1 + 0.1, zt)
    B.solid_box(0.5, y0 - 0.15, 2.9, y1 + 0.15, 0, 7)
    # the bird painting between the gable windows
    art(B, "art_bird", "x-", 0.5, 11.3, 15.2, 10.6, 13.6)
    B.lights.append((2.2, 13.25, 2.4, 0.5))


def art(B, mat, face, pos, a0, a1, z0, z1, th=0.1, frame="black"):
    """Framed picture on an axis-aligned wall. face names the wall it hangs on
    ('x-' = on the east wall facing west, etc.); a0..a1 is the run along it."""
    if face == "x-":
        B.box(frame, pos, a0, z0, pos + th, a1, z1, skip="x-x+")
        B.quad(mat, (pos + th, a1, z0), (pos + th, a0, z0), (pos + th, a0, z1), (pos + th, a1, z1), fit=(0, 0, 1, 1), flip=True)
    elif face == "x+":
        B.box(frame, pos - th, a0, z0, pos, a1, z1, skip="x-x+")
        B.quad(mat, (pos - th, a0, z0), (pos - th, a1, z0), (pos - th, a1, z1), (pos - th, a0, z1), fit=(0, 0, 1, 1), flip=True)
    elif face == "y-":
        B.box(frame, a0, pos, z0, a1, pos + th, z1, skip="y-y+")
        B.quad(mat, (a0, pos + th, z0), (a1, pos + th, z0), (a1, pos + th, z1), (a0, pos + th, z1), fit=(0, 0, 1, 1), flip=True)
    else:
        B.box(frame, a0, pos - th, z0, a1, pos, z1, skip="y-y+")
        B.quad(mat, (a1, pos - th, z0), (a0, pos - th, z0), (a0, pos - th, z1), (a1, pos - th, z1), fit=(0, 0, 1, 1), flip=True)


def baths_main(B):
    # ---- primary bath, 12'2" x 8'1": tub SW, shower SE, vanity NW, w.c. on the east wall
    x0, y0, x1, y1 = 33.7, 14.1, 45.8, 22.2
    tx, ty = 38.2, 18.5
    B.box("walltile", tx, ty, 0, x1, y1, 1.9, skip="z-x+y+")
    B.box("porcelain", tx + 0.5, ty + 0.4, 1.9, 45.0, 21.8, 1.95)
    tub = [(tx + 0.8, ty + 0.65), (44.7, ty + 0.65), (44.7, 21.55), (tx + 0.8, 21.55)]
    B.poly("porcelain", [(x, y, 0.6) for x, y in tub])
    for i in range(4):
        a, b = tub[i], tub[(i + 1) % 4]
        B.quad("porcelain", (a[0], a[1], 1.951), (b[0], b[1], 1.951), (b[0], b[1], 0.6), (a[0], a[1], 0.6))
    # wainscot photographed in listing photo 56, repeated every 3.7 ft
    B.quad("bath_wainscot", (x1, y1 - 0.01, 1.9), (tx, y1 - 0.01, 1.9), (tx, y1 - 0.01, 4.3), (x1, y1 - 0.01, 4.3), fit=(0, 0, (x1 - tx) / 3.7, 1))
    B.quad("bath_wainscot", (x1 - 0.01, ty, 1.9), (x1 - 0.01, y1, 1.9), (x1 - 0.01, y1, 4.3), (x1 - 0.01, ty, 4.3), fit=(0, 0, (y1 - ty) / 3.7, 1))
    # towel shelf over the tub and the small oak cabinet beside it, on the west wall
    B.quad("bath_shelf", (x1 - 0.02, 19.0, 4.6), (x1 - 0.02, 21.0, 4.6), (x1 - 0.02, 21.0, 6.5), (x1 - 0.02, 19.0, 6.5), fit=(0, 0, 1, 1))
    B.quad("bath_cabinet", (x1 - 0.02, 16.7, 4.3), (x1 - 0.02, 18.0, 4.3), (x1 - 0.02, 18.0, 6.3), (x1 - 0.02, 16.7, 6.3), fit=(0, 0, 1, 1))
    B.tube("chrome", (41.8, ty + 0.3, 1.95), (41.8, ty + 0.3, 2.4), 0.05)
    B.tube("chrome", (41.8, ty + 0.3, 2.4), (41.8, ty + 0.7, 2.3), 0.04)
    B.solid_box(tx, ty, x1, y1, 0, 3)
    # shower stall, south-east, with a wall between it and the tub
    sy, sx = 19.1, 37.6
    B.box("porcelain", x0, sy, 0, sx, y1, 0.3)
    B.box("porcelain", x0, sy, 0.3, x0 + 0.05, y1, 6.8, skip="x-")
    B.box("porcelain", x0, y1 - 0.05, 0.3, sx, y1, 6.8, skip="y+")
    B.box("paint_salt", sx, sy, 0, tx, y1, H1, skip="z-z+y+")
    B.quad("glass", (x0, sy + 0.05, 0.3), (sx, sy + 0.05, 0.3), (sx, sy + 0.05, 6.5), (x0, sy + 0.05, 6.5), grp="fx")
    B.beam("chrome", (x0, sy + 0.05, 6.5), (sx, sy + 0.05, 6.5), 0.08, 0.1)
    B.beam("chrome", (35.5, sy + 0.05, 0.3), (35.5, sy + 0.05, 6.5), 0.05, 0.05)
    B.tube("chrome", (x0 + 0.1, 20.7, 6.2), (x0 + 0.6, 20.7, 6.0), 0.04)
    B.solid_box(x0, sy, tx, y1, 0, 7)
    # double vanity on the north wall, west half
    vx = 39.6
    cabinet_run(B, vx, y0, x1, y0 + 1.8, 0, 2.75, "y+", 5, top="granite", drawers=False)
    for cxv in (41.1, 43.9):
        B.lathe("porcelain", (cxv, y0 + 0.9), [(0.72, 2.875), (0.55, 2.6), (0.1, 2.5)], n=16)
        B.tube("chrome", (cxv, y0 + 0.2, 2.87), (cxv, y0 + 0.2, 3.25), 0.035)
        B.tube("chrome", (cxv, y0 + 0.2, 3.25), (cxv, y0 + 0.6, 3.15), 0.03)
    B.box("oak", vx + 0.3, y0, 3.3, 45.2, y0 + 0.08, 6.6)
    B.quad("mirror", (vx + 0.55, y0 + 0.085, 3.55), (44.95, y0 + 0.085, 3.55), (44.95, y0 + 0.085, 6.35), (vx + 0.55, y0 + 0.085, 6.35), grp="fx")
    B.solid_box(vx, y0, x1, y0 + 1.85, 0, 3)
    toilet(B, 34.65, 16.0, -math.pi / 2)           # tank on the east wall, facing west
    for x, y in ((36.5, 17.5), (41.5, 17.2), (44.0, 20.4)):
        can_light(B, x, y, H1)
    # ---- half bath, 5'0" x 5'10": small vanity north-east, w.c. south-east under the window
    hx = SWX + 0.4
    cabinet_run(B, hx, 20.6, hx + 1.7, 22.6, 0, 2.75, "x+", 1, top="granite")
    B.lathe("porcelain", (hx + 0.9, 21.6), [(0.62, 2.875), (0.45, 2.6), (0.1, 2.5)], n=16)
    B.tube("chrome", (hx + 0.3, 21.6, 2.87), (hx + 0.3, 21.6, 3.25), 0.035)
    B.tube("chrome", (hx + 0.3, 21.6, 3.25), (hx + 0.7, 21.6, 3.15), 0.03)
    B.box("oak", hx, 20.7, 3.4, hx + 0.08, 22.5, 6.4)
    B.quad("mirror", (hx + 0.085, 22.3, 3.65), (hx + 0.085, 20.9, 3.65), (hx + 0.085, 20.9, 6.15), (hx + 0.085, 22.3, 6.15), grp="fx")
    B.solid_box(hx, 20.6, hx + 1.75, 22.6, 0, 3)
    toilet(B, hx + 1.15, 25.0, -math.pi / 2)
    can_light(B, 27.2, 23.4, H1)


def toilet(B, x, y, rot):
    """Two-piece toilet; rot=0 has the tank toward -y (bowl pointing +y)."""
    c, s = math.cos(rot), math.sin(rot)
    T = lambda dx, dy: (x + dx * c - dy * s, y + dx * s + dy * c)
    tx, ty = T(0, -0.75)
    hx, hy = abs(0.8 * c) + abs(0.33 * s), abs(0.8 * s) + abs(0.33 * c)
    B.box("porcelain", tx - hx, ty - hy, 1.15, tx + hx, ty + hy, 2.45)
    bx, by = T(0, 0.25)
    B.lathe("porcelain", (bx, by), [(0.35, 0), (0.42, 0.5), (0.62, 1.2), (0.66, 1.32), (0.5, 1.33), (0.4, 1.0)], n=16)
    B.lathe("porcelain", (bx, by), [(0.67, 1.33), (0.67, 1.4), (0.0, 1.4)], n=16)
    cs_ = [T(dx, dy) for dx in (-0.8, 0.8) for dy in (-1.1, 1.0)]
    B.solid_box(min(p[0] for p in cs_), min(p[1] for p in cs_), max(p[0] for p in cs_), max(p[1] for p in cs_), 0, 3)


# ----------------------------------------------------------------------------------
def stairs(B):
    """Straight flight over the basement stair, as photographed: an open oak stringer cut to the
    steps, two balusters standing on every tread, and a plain white wall closing the space below."""
    B.grp = "in"
    run = (SY1 - SY0) / (NR - 1)
    rise = F2 / NR
    xc = 20.2                      # centre line of the wall under the stair (plan)
    xe, xw = xc + 0.185, SX1       # treads span the wall's inner face to the west wall
    for i in range(NR - 1):
        y0 = SY0 + i * run
        z = (i + 1) * rise
        B.box("oak", xe - 0.42, y0 - 0.1, z - 0.1, xw, y0 + run, z)                             # tread, nosing returned over the stringer
        B.quad("oak", (xw, y0, z - rise), (xw, y0, z - 0.1), (xe, y0, z - 0.1), (xe, y0, z - rise))  # riser
    lower = lambda y: max(0.02, (y - SY0) / run * rise + rise - 1.05)       # underside of the stringer
    yb = SY0 + (1.05 - rise) * run / rise
    w = Wall(B, (xc, SY0 - 0.1), (xc, SY1), 0, F2, 0.37, "paint", "paint",
             top=[(0, 0.02), (yb - SY0 + 0.1, 0.02), (SY1 - SY0 + 0.1, lower(SY1))], solid=False)
    w.build()
    # the stringer: a sawtooth board on each face of that wall, from its top up to the treads
    saw = [(SY0 - 0.1, 0.0), (yb, 0.0), (SY1, lower(SY1))]
    for i in reversed(range(NR - 1)):
        saw += [(SY0 + (i + 1) * run, (i + 1) * rise - 0.1), (SY0 + i * run, (i + 1) * rise - 0.1)]
    saw.append((SY0 - 0.1, rise - 0.1))
    for xs in (xc - 0.2, xc + 0.2):
        B.poly("oak", [(xs, y, z) for y, z in saw])
    B.beam("oak", (xc - 0.21, yb, 0.05), (xc - 0.21, SY1, lower(SY1) + 0.03), 0.03, 0.12)      # bead along its lower edge
    # balusters on the treads, handrail and newels
    xr = xc - 0.05
    hz = lambda y: (y - SY0) / run * rise + rise + 2.75
    for i in range(NR - 1):
        for fr in (0.22, 0.72):
            y = SY0 + (i + fr) * run
            B.box("oak", xr - 0.05, y - 0.05, (i + 1) * rise, xr + 0.05, y + 0.05, hz(y) - 0.05, skip="z+z-", dens=6)
    B.beam("oak", (xr, SY0 - 0.35, hz(SY0 - 0.35)), (xr, SY1, hz(SY1)), 0.2, 0.16)
    B.box("oak", xr - 0.17, SY0 - 0.6, 0, xr + 0.17, SY0 - 0.26, hz(SY0 - 0.4) + 0.25)
    B.lathe("oak", (xr, SY0 - 0.43), [(0.0, hz(SY0 - 0.4) + 0.52), (0.2, hz(SY0 - 0.4) + 0.42), (0.24, hz(SY0 - 0.4) + 0.3), (0.12, hz(SY0 - 0.4) + 0.25)], n=12)
    B.box("oak", xr - 0.15, SY1 - 0.15, F2 - 0.6, xr + 0.15, SY1 + 0.15, F2 + 3.4)
    B.solid(xe - 0.1, SY0 - 0.6, xe - 0.1, SY1, 0, F2 + 3.5)
    B.beam("oak", (xw - 0.2, SY0, rise + 2.9), (xw - 0.2, SY1, F2 + 2.9), 0.13, 0.17)       # wall rail, west side
    B.floors.append({"poly": [[xe, SY0 - run], [SX1, SY0 - run], [SX1, SY1], [xe, SY1]],
                     "ramp": [SY0 - run, 0.0, SY1, F2]})


# ----------------------------------------------------------------------------------
def legacy_upper(B):
    """Sloped ceilings, dormers, the bath dormer wall, rails and upstairs fixtures."""
    B.grp = "in2"
    g = "in2"
    bx0, bx1, by0 = 20.4, 29.1, 16.85             # upstairs bath: east wall, west wall, north wall
    for (a, b), yf_ in zip(DORMERS[1:], DORMER_Y[1:]):      # dormer alcove floor beyond the plan's room outline
        flat(B, "carpet", a, yf_ + 0.2, b, yf_ + 2.5, F2 + 0.004)
        B.floor([(a, yf_ + 0.2), (b, yf_ + 0.2), (b, yf_ + 2.5), (a, yf_ + 2.5)], F2)
    nz = lambda y: EAVE + y
    sz = lambda y: EAVE + (D - y)
    yn, ys = CF - EAVE, D - (CF - EAVE)
    gn_, gs_ = GPK - EAVE, D - (GPK - EAVE)
    # the two slopes run a hair past the ridge so no crack can open between them
    slope(B, "ceiling", 0.5, SX0, 0.5, gn_ + 0.06, nz, holes=[(DORMERS[0][0], DORMERS[0][1], DORMER_Y[0] + 0.25, YD)], dens=14)
    slope(B, "ceiling", 0.5, SX0, gs_ - 0.06, D - 0.5, sz, dens=14, up=False)
    # owner: the only lights in the cathedral ceiling are the two fans and one track on the
    # south slope, four heads aimed into the kitchen
    # Fixture per the product listing: 24 in. matte-white bar on a round canopy, four
    # cylindrical heads. Position read from listing photograph 4fb1f0b7: mid-slope, just
    # east of the kitchen window, bar running east-west.
    import furnish
    from mathutils import Vector
    tx_, ty = 15.6, 19.3
    tz = EAVE + (D - ty)
    B.cyl("white", (tx_, ty), 0.24, tz - 0.1, tz + 0.15, n=16)
    B.tube("white", (tx_, ty, tz - 0.1), (tx_, ty, tz - 0.3), 0.03, n=6)
    B.tube("white", (tx_ - 1.0, ty, tz - 0.3), (tx_ + 1.0, ty, tz - 0.3), 0.035, n=8)
    aim = Vector((0.45, 0.35, -0.82)).normalized()       # down into the kitchen
    for hx_ in (tx_ - 0.85, tx_ - 0.28, tx_ + 0.28, tx_ + 0.85):
        top = Vector((hx_, ty, tz - 0.3))
        B.tube("white", top, top - Vector((0, 0, 0.12)), 0.02, n=6)
        a0 = top - Vector((0, 0, 0.12))
        B.tube("white", a0, a0 + aim * 0.36, 0.1, n=12)
        furnish.sphere(B, "lampglow", *(a0 + aim * 0.33), 0.085, n=8, grp="fx")
        B.lights.append((hx_ + 0.5, ty + 0.5, tz - 3.5, 0.15))
    B.poly("paint", [(SX0, yn, CF), (SX0, D / 2, GPK), (SX0, ys, CF)], dens=14)
    slope(B, "ceiling", SX0, W - 0.25, 0.5, yn, nz, holes=[(DORMERS[1][0], DORMERS[1][1], DORMER_Y[1] + 0.25, YD)], dens=14)
    flat(B, "ceiling", SX0, yn, W - 0.25, ys, CF, up=False, dens=14)
    slope(B, "ceiling", bx1, W - 0.25, ys, D - 0.5, sz, dens=14, up=False)
    slope(B, "ceiling", W - 0.25, GW - 0.5, 0.5, yn, nz, holes=[(DORMERS[2][0], DORMERS[2][1], DORMER_Y[2] + 0.25, YD)], dens=14)
    flat(B, "ceiling", W - 0.25, yn, GW - 0.5, ys, CF, up=False, dens=14)
    slope(B, "ceiling", W - 0.25, GW - 0.5, ys, D - 0.5, sz, dens=14, up=False)
    flat(B, "ceiling", bx0, ys, bx1, D - 0.5, CF - 0.01, up=False)
    for i, (a, b) in enumerate(DORMERS):
        m = "paint" if i < 2 else "paint_sage"
        kn = (0, KNL, KNB)[i]
        yf = DORMER_Y[i]                    # centre line of the dormer's front wall
        yi = yf + 0.25                      # its inside face
        flat(B, "ceiling", a, yi, b, YD, ZD, up=False)
        for x, fl in ((a, False), (b, True)):
            if i == 0:
                pts = [(x, yi, EAVE + yi), (x, YD, ZD), (x, yi, ZD)]
            else:
                pts = [(x, yi, F2), (x, kn, F2), (x, kn, EAVE + kn), (x, YD, ZD), (x, yi, ZD)]
            B.poly(m, pts, flip=fl)
        if i:
            B.solid(a, yi, a, kn, F2, F2 + 7)
            B.solid(b, yi, b, kn, F2, F2 + 7)
        # dormer front wall with its window
        dw = Wall(B, (a - 0.4, yf), (b + 0.4, yf), (EAVE + yf) if i == 0 else F2, ZD + 0.3, 0.5, m, "siding",
                  grp="in" if i == 0 else g, grpR="ex", ends=False, solid=bool(i),
                  top=[(0, ZD + 0.3), ((b - a) / 2 + 0.4, ZD + 0.3 + (b - a) / 2 + 0.4), (b - a + 0.8, ZD + 0.3)])
        z0 = 12.2 if i == 0 else 11.9
        window(B, dw, 0.9, b - a - 0.1, z0, z0 + 3.3, units=1, grid=(3, 2), grp_in="in" if i == 0 else g)
        dw.build()
    # the bath sits in a shed dormer: its south wall rises from the house wall
    bs = Wall(B, (bx1 + 0.2, D - 0.25), (bx0 - 0.2, D - 0.25), F2, CF, 0.5, "paint_salt", "siding", grp=g, grpR="ex", ends=False)
    window(B, bs, bx1 + 0.2 - 25.9, bx1 + 0.2 - 23.5, F2 + 3.0, F2 + 6.4, units=1, grp_in=g)
    bs.build()
    bath_upper(B)
    # guard rails: loft edge over the kitchen, and the west side of the stair well
    rail(B, (SX0 + 0.15, SY1 + 0.25, F2), (SX0 + 0.15, by0 + 0.2, F2), h=3.0, grp=g, newels=(False, False))
    rail(B, (SWX + 0.2, KNL + 0.2, F2), (SWX + 0.2, SY1, F2), h=3.0, grp=g, newels=(True, True))
    for x, y in ((28, 9), (34, 9), (28, 14), (34, 14), (41, 9), (41, 14), (52, 16.5), (58, 11), (64, 16), (58, 18), (64, 9.5),
                 (24.7, 19.5)):
        can_light(B, x, y, CF)


def bath_upper(B):
    """Vanity then w.c. along the east wall, tub south-west, linen closets north-west (drawn feet)."""
    g = "in2"
    z = F2
    x0, x1, y0, y1 = 20.6, 28.9, 16.9, D - 0.5
    cabinet_run(B, x0, y0, x0 + 1.9, 22.1, z, z + 2.75, "x+", 4, top="granite", grp=g)
    B.lathe("porcelain", (x0 + 0.95, 19.4), [(0.7, z + 2.875), (0.5, z + 2.6), (0.1, z + 2.5)], n=16)
    B.tube("chrome", (x0 + 0.25, 19.4, z + 2.87), (x0 + 0.25, 19.4, z + 3.25), 0.035)
    B.tube("chrome", (x0 + 0.25, 19.4, z + 3.25), (x0 + 0.6, 19.4, z + 3.15), 0.03)
    B.box("oak", x0, y0 + 0.2, z + 3.3, x0 + 0.08, 21.9, z + 6.5)
    B.quad("mirror", (x0 + 0.085, 21.7, z + 3.5), (x0 + 0.085, y0 + 0.4, z + 3.5), (x0 + 0.085, y0 + 0.4, z + 6.3), (x0 + 0.085, 21.7, z + 6.3), grp="fx")
    B.solid_box(x0, y0, x0 + 1.95, 22.1, z, z + 3)
    n0 = len(B.surfs)
    toilet(B, x0 + 1.15, 24.5, -math.pi / 2)
    for sf in B.surfs[n0:]:                       # the toilet helper builds at the main floor
        sf.verts = [v + UP * z for v in sf.verts]
        sf.grp = g
    B.solids[-4:] = [(s_[0], s_[1], s_[2], s_[3], z, z + 3) for s_ in B.solids[-4:]]
    tx, ty = 26.4, 21.3                           # tub / shower in the south-west corner
    B.box("porcelain", tx, ty, z, x1, y1, z + 1.6, skip="z-")
    B.box("porcelain", x1 - 0.1, ty, z + 1.6, x1, y1, z + 7.0)
    B.box("porcelain", tx, y1 - 0.1, z + 1.6, x1, y1, z + 7.0)
    B.box("porcelain", tx, ty, z + 1.6, x1, ty + 0.1, z + 7.0)
    B.tube("chrome", (tx - 0.05, ty, z + 6.6), (tx - 0.05, y1, z + 6.6), 0.04)
    B.quad("linen", (tx - 0.1, 23.6, z + 0.3), (tx - 0.1, y1, z + 0.3), (tx - 0.1, y1, z + 6.6), (tx - 0.1, 23.6, z + 6.6))
    B.solid_box(tx, ty, x1, y1, z, z + 7)
    for x, y in ((24.4, 18.8), (24.4, 23.6)):
        can_light(B, x, y, CF - 0.01)


def roof(B):
    B.grp = "ex"
    B.dens = 6
    ov = 1.2
    x0, x1 = -ov, GW + ov
    # north slope with dormer holes, south slope with the bath dormer notch
    slope(B, "roof", x0, x1, -ov, RIDGE, zr, holes=[(a - 0.4, b + 0.4, yf_ - 0.25, ZD - EAVE - 1.0) for (a, b), yf_ in zip(DORMERS, DORMER_Y)], up=True, uvrot=False)
    slope(B, "roof", x0, 20.4, RIDGE, D + ov, zr, up=True)
    slope(B, "roof", 29.3, x1, RIDGE, D + ov, zr, up=True)
    slope(B, "roof", 20.4, 29.3, RIDGE, 17.2, zr, up=True)
    # soffits / fascia and rake boards
    for y, s in ((-ov, -1), (D + ov, 1)):
        B.quad("extrim", (x0, y, zr(y) - 0.02), (x1, y, zr(y) - 0.02), (x1, y, zr(y) - 0.75), (x0, y, zr(y) - 0.75), flip=(s > 0))
        ya, yb = (y, y + ov) if s < 0 else (y - ov, y)
        flat(B, "extrim", x0, ya, x1, yb, zr(y) - 0.75, up=False)
    for x, fl in ((x0, False), (x1, True)):
        for ya, yb in ((-ov, RIDGE), (RIDGE, D + ov)):
            B.quad("extrim", (x, ya, zr(ya) - 0.75), (x, yb, zr(yb) - 0.75), (x, yb, zr(yb)), (x, ya, zr(ya)), flip=fl)
            xi = x + (ov if x < 0 else -ov)
            B.quad("extrim", (min(x, xi), ya, zr(ya) - 0.75), (max(x, xi), ya, zr(ya) - 0.75), (max(x, xi), yb, zr(yb) - 0.75), (min(x, xi), yb, zr(yb) - 0.75), flip=True)
    # north dormers: cheeks and a small gable roof dying into the main slope
    for (a, b), yf_ in zip(DORMERS, DORMER_Y):
        ax, bx = a - 0.4, b + 0.4
        zt = ZD + 0.3
        hw = (bx - ax) / 2
        pk = zt + hw
        xm = (ax + bx) / 2
        e = 0.5
        rz = EAVE + 1.0                      # main roof height at y = 0
        yo = yf_ - 0.25                      # outside face of the dormer's front wall
        for x in (ax, bx):
            B.poly("siding", [(x, yo, rz + yo - 0.3), (x, yo, zt), (x, zt - rz, zt)])
        ze = zt - e
        for xe in (ax - e, bx + e):
            B.poly("roof", [(xe, yo - 0.9, ze + 0.25), (xm, yo - 0.9, pk + 0.25), (xm, pk + 0.25 - rz, pk + 0.25), (xe, ze + 0.25 - rz, ze + 0.25)])
            B.poly("extrim", [(xe, yo - 0.9, ze + 0.2), (xm, yo - 0.9, pk + 0.2), (xm, yo - 0.9, pk - 0.35), (xe, yo - 0.9, ze - 0.35)])
            B.poly("extrim", [(xe, yo - 0.9, ze + 0.2), (xm, yo - 0.9, pk + 0.2), (xm, yo, pk + 0.2), (xe, yo, ze + 0.2)])
    # bath shed dormer on the south slope
    zs0, zs1 = 19.2, 17.7
    B.quad("roof", (20.0, 17.0, zs0), (29.7, 17.0, zs0), (29.7, D + 1.0, zs1), (20.0, D + 1.0, zs1))
    B.quad("extrim", (20.0, D + 1.0, zs1), (29.7, D + 1.0, zs1), (29.7, D + 1.0, zs1 - 0.5), (20.0, D + 1.0, zs1 - 0.5), flip=True)
    for x, fl in ((20.4, False), (29.3, True)):
        B.poly("siding", [(x, 17.2, zr(17.2)), (x, D, EAVE), (x, D, zs1 - 0.1), (x, 17.2, zs0 - 0.02)], flip=fl)
    B.quad("siding", (20.4, D, CF), (29.3, D, CF), (29.3, D, zs1), (20.4, D, zs1), flip=True)
    B.dens = 20


def exterior(B):
    B.grp = "ex"
    B.dens = 8
    # stone base and wainscot along the front, full stone behind the entry porch
    B.box("stone", -0.12, -0.14, BASE, 16.5, 0.0, 2.0, skip="y+z-")
    B.box("stone", 16.5, -0.14, BASE, 20.4, 0.0, 8.4, skip="y+z-")      # either side of the front door
    B.box("stone", 24.0, -0.14, BASE, 28.5, 0.0, 8.4, skip="y+z-")
    B.box("stone", 20.4, -0.14, 7.1, 24.0, 0.0, 8.4, skip="y+")        # and over it
    B.box("stone", 28.5, -0.14, BASE, W, 0.0, 2.0, skip="y+z-")
    for a in (W, 57.6, 68.2):
        b = {W: 48.6, 57.6: 59.2, 68.2: GW + 0.12}[a]
        B.box("stone", a, -0.14, GROUND_N - 1, b, 0.0, 1.6, skip="y+z-")
    # re-open the stone where it would cover the windows / door
    # (stone stops at sill height 2.3 > 3.0? keep wainscot below the sills)
    # foundation: parged block on the downhill sides
    B.box("parge", -0.02, 0.0, BASE, W, D + 0.02, -0.02, skip="z-z+y-")
    B.box("stone", -0.14, 0.0, BASE, 0.0, D, 0.0, skip="x+z-")
    B.box("parge", GW - 0.02, 0.0, BASE, GW + 0.03, D, GROUND_N, skip="z-x-")
    # chimney: full-height stone stack outside the east wall
    B.box("stone", -2.6, 9.6, BASE, 0.0, 16.9, 9.5, skip="x+z-")
    B.poly("stone", [(-2.6, 9.6, 9.5), (0, 9.6, 9.5), (0, 10.6, 12.0), (-2.2, 10.6, 12.0)])
    B.poly("stone", [(0, 16.9, 9.5), (-2.6, 16.9, 9.5), (-2.2, 15.9, 12.0), (0, 15.9, 12.0)])
    B.poly("stone", [(-2.6, 16.9, 9.5), (-2.6, 9.6, 9.5), (-2.2, 10.6, 12.0), (-2.2, 15.9, 12.0)])
    B.box("stone", -2.2, 10.6, 12.0, 0.0, 15.9, 27.5, skip="z-")
    # the stack's inboard face above the roof, stepped to the roof slope so that none of it
    # hangs below the cathedral ceiling (it used to show as a stray triangle at the gable peak)
    yy = 10.6
    while yy < 15.9 - 1e-6:
        y2 = min(15.9, yy + 0.5)
        B.box("stone", 0.0, yy, min(zr(yy), zr(y2)) - 0.3, 1.6, y2, 27.5, skip="z-x-")
        yy = y2
    B.box("concrete", -2.4, 10.4, 27.5, 1.8, 16.1, 27.8)
    B.solid_box(-2.6, 9.6, 0.0, 16.9, -1, 9)
    # front entry porch
    px0, px1, py = 16.5, 28.5, -6.0
    B.box("concrete", px0, py, GROUND_N - 1, px1, 0.0, -0.5, skip="z-")
    B.box("concrete", 20.0, py - 1.4, GROUND_N - 1, 25.0, py, -1.05, skip="z-")
    B.floor([(px0, py), (px1, py), (px1, 0.4), (px0, 0.4)], -0.5)
    B.floor([(20.0, py - 1.4), (25.0, py - 1.4), (25.0, py), (20.0, py)], -1.05)
    B.floor([(20.6, -0.3), (24.1, -0.3), (24.1, 0.6), (20.6, 0.6)], -0.2)
    posts = (px0 + 0.25, 20.0, 25.0, px1 - 0.25)
    for x in posts:
        B.box("deckstain", x - 0.25, py + 0.05, -0.5, x + 0.25, py + 0.55, 7.9, skip="z-z+")
        B.solid_box(x - 0.25, py + 0.05, x + 0.25, py + 0.55, -1, 8)
    for xa, xb in ((posts[0], posts[1]), (posts[2], posts[3])):
        rail(B, (xa + 0.25, py + 0.3, -0.5), (xb - 0.25, py + 0.3, -0.5), h=2.6, mat="deckstain", newels=(False, False), bal=0.12, top=(0.3, 0.13))
    for x in (px0 + 0.25, px1 - 0.25):
        rail(B, (x, py + 0.55, -0.5), (x, -0.15, -0.5), h=2.6, mat="deckstain", newels=(False, False), bal=0.12, top=(0.3, 0.13))
    B.box("deckstain", px0 - 0.1, py, 7.9, px1 + 0.1, py + 0.6, 8.7)
    for x in (px0 - 0.1, px1 - 0.5):
        B.box("deckstain", x, py + 0.6, 7.9, x + 0.6, 0.0, 8.7)
    flat(B, "cedar", px0, py + 0.6, px1, 0.0, 8.5, up=False)
    hw = (px1 - px0) / 2 + 0.6
    xm = (px0 + px1) / 2
    ze = 8.7
    pk = ze + hw
    # gable face with the star
    B.poly("siding", [(px0 - 0.1, py + 0.02, ze), (xm, py + 0.02, pk - 0.1), (px1 + 0.1, py + 0.02, ze)])
    B.cyl("extrim", (xm, py - 0.03), 0.0, 0, 0) if False else None
    star = []
    for i in range(10):
        r = 1.5 if i % 2 == 0 else 0.6
        a = math.pi / 2 + i * math.pi / 5
        star.append((xm + r * math.cos(a), py - 0.02, 11.4 + r * math.sin(a)))
    B.poly("extrim", star, flip=False)
    B.poly("extrim", star, flip=True)
    yf = py - 1.0
    for sx, fl in ((-1, True), (1, False)):
        xe = xm + sx * (hw + 0.7)
        zee = ze - 0.7 + 0.3
        B.poly("roof", [(xe, yf, zee), (xm, yf, pk + 0.3), (xm, pk + 0.3 - (EAVE + 1.0), pk + 0.3), (xe, zee - (EAVE + 1.0), zee)], flip=fl)
        B.poly("extrim", [(xe, yf, zee - 0.05), (xm, yf, pk + 0.25), (xm, py, pk + 0.25), (xe, py, zee - 0.05)], flip=not fl)
        B.poly("extrim", [(xe, yf, zee - 0.05), (xm, yf, pk + 0.25), (xm, yf, pk - 0.4), (xe, yf, zee - 0.6)], flip=not fl)
    # paver walk and gravel drive
    flat(B, "pavers", 6.0, py - 5.4, 40.0, py - 1.4, GROUND_N + 0.03)
    flat(B, "pavers", 20.0, py - 1.4, 25.0, py - 1.39, GROUND_N + 0.03)
    flat(B, "gravel", 40.0, -42.0, GW + 14.0, 0.0, GROUND_N + 0.02)
    flat(B, "gravel", 46.0, -140.0, 62.0, -42.0, GROUND_N + 0.02)
    B.dens = 20


def porch_and_deck(B):
    B.grp = "ex"
    B.dens = 10
    zf = -0.25
    py0, py1 = D, D + 7.6
    # ---- screened back porch ----
    flat(B, "deck", 0.0, py0, W, py1, zf, uvrot=True, dens=16)
    B.floor([(0.0, py0 - 0.6), (W, py0 - 0.6), (W, py1), (0.0, py1)], zf)
    B.box("deckstain", 0.0, py1 - 0.1, zf - 0.9, W, py1, zf, skip="z+")
    flat(B, "cedar", 0.0, py0, W, py1, 8.6, up=False, dens=12)
    # porch back wall is the house siding (already built). Posts along the outer edge.
    xs = [0.25 + i * (W - 0.5) / 6 for i in range(7)]
    for x in xs:
        B.box("deckstain", x - 0.25, py1 - 0.5, BASE, x + 0.25, py1, 8.6, skip="z-z+")
    B.box("deckstain", 0.0, py1 - 0.55, 7.8, W, py1 + 0.05, 8.6)
    for a, b in zip(xs, xs[1:]):
        rail(B, (a + 0.25, py1 - 0.25, zf), (b - 0.25, py1 - 0.25, zf), h=3.0, mat="deckstain", newels=(False, False), bal=0.12, top=(0.3, 0.13), spacing=0.45)
        B.quad("screen", (a + 0.25, py1 - 0.2, zf + 3.0), (b - 0.25, py1 - 0.2, zf + 3.0), (b - 0.25, py1 - 0.2, 7.8), (a + 0.25, py1 - 0.2, 7.8), grp="fx")
    # west end: screened, with the closed porch door to the outside steps
    B.box("deckstain", W - 0.4, py0, zf, W, py0 + 0.4, 8.6, skip="z-z+")
    gy0, gy1 = py0 + 0.9, py0 + 3.6                 # the porch's west door, per the plan
    rail(B, (W - 0.2, py0 + 0.4, zf), (W - 0.2, gy0, zf), h=3.0, mat="deckstain", newels=(False, True), bal=0.12, top=(0.3, 0.13))
    rail(B, (W - 0.2, gy1, zf), (W - 0.2, py1 - 0.5, zf), h=3.0, mat="deckstain", newels=(True, False), bal=0.12, top=(0.3, 0.13))
    for i in range(4):                                    # steps down to the west side yard
        x0_, z_ = W + i * 1.1, zf - (i + 1) * 0.6
        B.box("deckstain", x0_, gy0, z_ - 0.6, x0_ + 1.1, gy1, z_, skip="z-", mats={"z+": "deck"})
        B.floor([(x0_ - (0.3 if i == 0 else 0), gy0), (x0_ + 1.1, gy0), (x0_ + 1.1, gy1), (x0_ - (0.3 if i == 0 else 0), gy1)], z_)
    B.box("deckstain", W - 0.4, py0, 7.8, W, py1, 8.6)
    # east end: framed opening with the screen door (open) onto the deck
    B.box("deckstain", 0.0, py0 + 0.0, zf, 0.4, py0 + 3.2, 8.6, skip="z-z+")
    B.box("deckstain", 0.0, py0 + 6.2, zf, 0.4, py1 - 0.5, 8.6, skip="z-z+")
    B.box("deckstain", 0.0, py0 + 3.2, 6.9, 0.4, py0 + 6.2, 8.6)
    B.solid(0.2, py0, 0.2, py0 + 3.2, zf, 8)
    B.solid(0.2, py0 + 6.2, 0.2, py1, zf, 8)
    # porch roof: shallow shed from the main eave
    B.quad("roof", (-1.2, py0 - 1.0, EAVE + 2.0), (W + 0.5, py0 - 1.0, EAVE + 2.0), (W + 0.5, py1 + 1.2, 9.2), (-1.2, py1 + 1.2, 9.2), dens=6)
    B.quad("extrim", (-1.2, py1 + 1.2, 9.2), (W + 0.5, py1 + 1.2, 9.2), (W + 0.5, py1 + 1.2, 8.6), (-1.2, py1 + 1.2, 8.6), flip=True)
    flat(B, "extrim", -1.2, py1, W + 0.5, py1 + 1.2, 8.6, up=False)
    for x, fl in ((-1.2, False), (W + 0.5, True)):
        B.poly("extrim", [(x, py0 - 1.0, EAVE + 2.0), (x, py1 + 1.2, 9.2), (x, py1 + 1.2, 8.6), (x, py0 - 1.0, 8.6)], flip=fl)
    B.poly("siding", [(0.0, py0, 8.6), (0.0, py1, 8.6), (0.0, py1, 9.3), (0.0, py0, EAVE + 1.9)], flip=True)
    # ceiling fan and cans
    for x in (8.0, 23.0, 38.0):
        can_light(B, x, py0 + 3.8, 8.6)
    # ---- open deck on the east side ----
    dx0, dx1, dy0, dy1 = -11.9, 0.0, 0.0, py1
    flat(B, "deck", dx0, dy0, dx1, dy1, zf, dens=16)
    B.floor([(dx0, dy0), (dx1 + 0.6, dy0), (dx1 + 0.6, dy1), (dx0, dy1)], zf)
    B.box("deckstain", dx0, dy0, zf - 0.9, dx1, dy1, zf, skip="z+x+")
    # rail posts and guard rails; lattice privacy screen along the north edge
    for (ax, ay, bx, by) in ((dx0, dy0, dx0, dy1), (dx0, dy1, dx1, dy1)):
        n = max(1, int(round(math.hypot(bx - ax, by - ay) / 6.0)))
        for i in range(n):
            a = Vector((ax + (bx - ax) * i / n, ay + (by - ay) * i / n, zf))
            b = Vector((ax + (bx - ax) * (i + 1) / n, ay + (by - ay) * (i + 1) / n, zf))
            rail(B, a, b, h=3.0, mat="deckstain", newels=(True, i == n - 1), bal=0.12, top=(0.3, 0.13), newel=0.33, cap=0.15, spacing=0.45)
    for x in (dx0, dx0 / 2, dx1 - 0.3):
        B.box("deckstain", x - 0.17, dy0 - 0.17, zf, x + 0.17, dy0 + 0.17, zf + 3.6, skip="z-")
    B.box("deckstain", dx0, dy0 - 0.1, zf + 3.3, dx1, dy0 + 0.1, zf + 3.5)
    B.quad("lattice", (dx0, dy0, zf), (dx1, dy0, zf), (dx1, dy0, zf + 3.3), (dx0, dy0, zf + 3.3), grp="fx")
    B.solid(dx0, dy0, dx1, dy0, zf, zf + 3.5)
    # deck structure: posts and lattice skirt down to grade
    for x in (dx0 + 0.2,):
        for y in [dy0 + 0.2 + i * (dy1 - dy0 - 0.4) / 5 for i in range(6)]:
            B.box("deckstain", x - 0.25, y - 0.25, BASE - 4, x + 0.25, y + 0.25, zf - 0.9, skip="z-z+")
    B.quad("lattice", (dx0, dy0, zf - 0.9), (dx0, dy0, -12), (dx1, dy0, -12), (dx1, dy0, zf - 0.9), grp="fx")
    B.quad("lattice", (dx0, dy1 * 0.45, zf - 0.9), (dx0, dy1 * 0.45, -12), (dx0, dy0, -12), (dx0, dy0, zf - 0.9), grp="fx")
    # hot tub in the south-east corner
    # Hot Spring Flair (7 ft square) in the outer south corner, with room behind it for the cover
    hx0, hy0, hx1, hy1 = -11.4, 23.9, -4.4, 30.7
    B.box("tubshell", hx0, hy0, zf, hx1, hy1, zf + 2.9, skip="z-z+")
    B.box("porcelain", hx0 - 0.08, hy0 - 0.08, zf + 2.9, hx1 + 0.08, hy1 + 0.08, zf + 3.1, skip="z-")
    flat(B, "water", hx0 + 0.7, hy0 + 0.7, hx1 - 0.7, hy1 - 0.7, zf + 3.105, grp="fx")
    B.solid_box(hx0, hy0, hx1, hy1, zf, zf + 3.2)
    B.dens = 20


def ground(x, y):
    """Grade around the house: level at the front, falling to the walkout side."""
    s = lambda t: max(0.0, min(1.0, t)) ** 2 * (3 - 2 * max(0.0, min(1.0, t)))
    h = GROUND_N - 8.0 * s((y - 1.0) / 34.0) * (1.0 - 0.85 * s((x - 44.0) / 7.0)) - 4.5 * s((-x - 2.0) / 45.0) * s((y + 30) / 40.0)
    h -= 0.05 * max(0.0, -y - 10) + 0.12 * max(0.0, y - 36.0)
    far = math.hypot(x - 30, y - 13)
    h += 22.0 * s((far - 230.0) / 100.0)
    h += 0.6 * math.sin(x * 0.045) * math.cos(y * 0.05) * min(1.0, max(0.0, (abs(y - 13) - 50) / 50 + (abs(x - 30) - 60) / 60))
    return h


def site(B):
    """Terrain as one warped grid per ground cover, finer near the house."""
    from hb import Surf
    B.grp = "ex"
    R, N = 330.0, 96
    f = lambda t: (t * 2 - 1) ** 3 * 0.65 + (t * 2 - 1) * 0.35
    lawn = lambda x, y: (-62 < y < 3 and -20 < x < 46) or (3 <= y < 62 and -36 < x < -9)
    xs = [30 + R * f(i / N) for i in range(N + 1)]
    ys = [13 + R * f(j / N) for j in range(N + 1)]
    cell = 2 * R / N
    for mat in ("grass", "leaves"):
        s = Surf()
        s.mat, s.grp, s.dens = mat, "ex", 2.6
        s.verts, s.tris, s.uv0, s.lm, s.nrm = [], [], [], [], []
        t = MATS[mat]["tile"]
        for j in range(N + 1):
            for i in range(N + 1):
                x, y = xs[i], ys[j]
                e = 0.5
                n = Vector((ground(x - e, y) - ground(x + e, y), ground(x, y - e) - ground(x, y + e), 2 * e)).normalized()
                s.verts.append(Vector((x, y, ground(x, y))))
                s.nrm.append(n)
                s.uv0.append((x / t, y / t))
                s.lm.append((i * cell * 0.5, j * cell * 0.5))
        for j in range(N):
            for i in range(N):
                cx, cy = (xs[i] + xs[i + 1]) / 2, (ys[j] + ys[j + 1]) / 2
                if (mat == "grass") != bool(lawn(cx, cy)):
                    continue
                if 3.0 < cx < GW - 3 and 3.0 < cy < D - 3:
                    continue
                a, b, c, d = j * (N + 1) + i, j * (N + 1) + i + 1, (j + 1) * (N + 1) + i + 1, (j + 1) * (N + 1) + i
                s.tris += [(a, b, c), (a, c, d)]
        s.w = s.h = N * cell * 0.5
        B.surfs.append(s)
    B.ground = ground
    trees(B)


def trees(B):
    """Hardwood stand around the clearing: bark trunks with crossed canopy cards."""
    import random
    rnd = random.Random(323)
    placed = []
    def clear(x, y):
        if -16 < x < GW + 8 and -12 < y < D + 16: return False          # house, deck, porch
        if 38 < x < GW + 16 and -46 < y < 2: return False                # parking apron
        if 44 < x < 64 and y < -40: return False                         # drive
        if -16 < x < 46 and -30 < y < 0: return False                    # front lawn stays open
        return all((x - a) ** 2 + (y - b) ** 2 > 81 for a, b in placed)
    want = 230
    tries = 0
    while len(placed) < want and tries < 20000:
        tries += 1
        r = 14 + 250 * rnd.random() ** 0.8
        a = rnd.random() * 2 * math.pi
        x, y = 30 + r * math.cos(a), 13 + r * math.sin(a)
        if not clear(x, y):
            continue
        placed.append((x, y))
        g = ground(x, y)
        small = rnd.random() < 0.3
        ht = rnd.uniform(16, 26) if small else rnd.uniform(48, 72)
        rad = ht * 0.008 + 0.22
        base = ht * (0.3 if small else 0.5)
        B.lathe("bark", (x, y), [(rad * 1.25, g - 1.0), (rad, g + 3.0), (rad * 0.6, g + ht * 0.85)], n=7, grp="ex", dens=1.5)
        cw = ht * (0.42 if small else 0.34)
        rot = rnd.random() * math.pi
        for k in range(2):
            c, s_ = math.cos(rot + k * math.pi / 2), math.sin(rot + k * math.pi / 2)
            fl = rnd.random() < 0.5
            u0, u1 = (1, 0) if fl else (0, 1)
            B.poly("canopy", [(x - c * cw, y - s_ * cw, g + base), (x + c * cw, y + s_ * cw, g + base),
                              (x + c * cw, y + s_ * cw, g + ht * 1.08), (x - c * cw, y - s_ * cw, g + ht * 1.08)],
                   fit=(u0, 0, u1, 1), grp="fx")
        if r < 120:
            B.solid_box(x - rad, y - rad, x + rad, y + rad, g - 2, g + 12)
