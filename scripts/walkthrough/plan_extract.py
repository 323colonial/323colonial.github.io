"""Turn the floor-plan SVGs of the listing's 3D tour into plan.json (model feet).

    python3 scripts/walkthrough/plan_extract.py MAIN.svg UPPER.svg > scripts/walkthrough/plan.json

The SVGs are zillowstatic.com/floor_map/<id>/floor_shape/<floor>/compressed.svg, in metres.
Model frame: x = feet west of the east wall's outer face, y = feet south of the front wall's
outer face. The upper-floor scan is about 3% narrower than the main one and is fitted to it
(inner faces of the two end walls, and the bath's south wall flush with the house wall).
"""
import json, re, sys

FT = 0.3048
XF = {"main": (1.0, 28.8, 17.7), "upper": (69.1 / 67.2, 0.5 + 38.8 * 69.1 / 67.2, 13.3)}


def pts(s, floor):
    sx, ox, oy = XF[floor]
    n = [float(v) for v in re.findall(r"-?\d+\.?\d*(?:e-?\d+)?", s)]
    return [[round(n[i] / FT * sx + ox, 2), round(n[i + 1] / FT + oy, 2)] for i in range(0, len(n) - 1, 2)]


def section(v, name, nxt):
    i = v.find('<g id="%s"' % name)
    return v[i:v.find('<g id="%s"' % nxt, i + 1)]


out = {"rooms": [], "walls": [], "doors": [], "windows": []}
for floor, path in (("main", sys.argv[1]), ("upper", sys.argv[2])):
    v = open(path).read()
    names = {}
    for rid, body in re.findall(r'class="note" data-room="([0-9a-f]+)">(.*?)</g></g></g>', v, re.S):
        t = re.findall(r'<text style="font-size:0\.239px">([^<]+)</text>', body)
        if t:
            names[rid] = (names.get(rid, "") + " " + t[0]).strip()
    for rid, body in re.findall(r'<g id="([0-9a-f]+)"[^>]*>(.*?)</g>', section(v, "roomShapes", "spiralStaircases"), re.S):
        p = re.findall(r'points="([^"]+)"', body) or re.findall(r' d="([^"]+)"', body)
        if p:
            out["rooms"].append({"floor": floor, "name": names.get(rid, ""), "poly": pts(p[0], floor)})
    for kind, a, b in (("walls", "walls", "doors"), ("doors", "doors", "windows"), ("windows", "windows", "footprint")):
        for gid, body in re.findall(r'<g id="([^"]+)"[^>]*>(.*?)</g>', section(v, a, b), re.S):
            p = re.findall(r'points="([^"]+)"', body)
            if p and gid not in ("walls", "doors", "windows"):
                out[kind].append({"floor": floor, "poly": pts(p[0], floor)})
            elif p:
                out[kind].append({"floor": floor, "poly": pts(p[0], floor)})
json.dump(out, sys.stdout, separators=(",", ":"))
