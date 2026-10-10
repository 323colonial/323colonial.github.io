"""Build, preview, bake and export the 323 Colonial walkthrough model.

    blender -b -P scripts/walkthrough/build.py -- --work DIR [--preview] [--bake] [--export]

--work DIR   scratch directory holding textures/ and the HDRI; outputs land in it
--preview    render reference stills from the listing-photo viewpoints
--bake       bake Cycles irradiance into the lightmap atlas pages
--export     write house.glb, scene.json (materials, collision, spawn)
"""
import bpy, sys, os, math, json, time, importlib
import numpy as np
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import hb, parts, furnish, house
for m in (hb, parts, furnish, house):
    importlib.reload(m)

FT = 0.3048
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
opt = lambda k, d=None: (argv[argv.index(k) + 1] if k in argv and d is not None else (k in argv)) if (k in argv or d is None) else d
WORK = opt("--work", "/tmp/colonial")
TEX = os.path.join(WORK, "textures")
HDRI = os.path.join(WORK, "sky.hdr")
SIZE = int(opt("--size", "4096"))
SAMPLES = int(opt("--samples", "256"))
LM_RANGE = 4.0
SUN_ROT = math.radians(float(opt("--sunrot", "77")))   # rotation of the sky about Z

try:
    os.nice(10)      # run below normal priority so a bake does not drag the rest of the machine
except OSError:
    pass
t0 = time.time()
log = lambda *a: print("[%6.1fs]" % (time.time() - t0), *a, flush=True)


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        # GPU only: with the CPU also enabled as a render device the bake ran almost
        # entirely on the CPU cores and left the GPU idle
        for d in prefs.devices:
            d.use = d.type != "CPU"
        sc.cycles.device = "GPU"
        log("render devices:", [(d.name, d.type, d.use) for d in prefs.devices])
    except Exception as e:
        log("GPU unavailable:", e)
    # leave a few cores free so the machine stays responsive while baking
    sc.render.threads_mode = "FIXED"
    sc.render.threads = max(2, (os.cpu_count() or 8) - 4)
    sc.unit_settings.system = "METRIC"
    return sc


def image(name):
    for ext in (".jpg", ".png"):
        p = os.path.join(TEX, name + ext)
        if os.path.exists(p):
            return bpy.data.images.load(p, check_existing=True)
    return None


def make_material(name, spec, page_img):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    col = tuple(spec.get("color", (1, 1, 1))) + (1,)
    img = image(spec["tex"]) if spec.get("tex") else None
    uv = nt.nodes.new("ShaderNodeUVMap")
    uv.uv_map = "uv0"
    base = None
    alpha = None
    if img:
        tx = nt.nodes.new("ShaderNodeTexImage")
        tx.image = img
        nt.links.new(uv.outputs[0], tx.inputs[0])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs[0].default_value = 1.0
        nt.links.new(tx.outputs[0], mix.inputs[6])
        mix.inputs[7].default_value = col
        base = mix.outputs[2]
        if spec.get("alpha"):
            alpha = tx.outputs[1]
    if spec.get("glass") or spec.get("screen"):
        sh = nt.nodes.new("ShaderNodeBsdfTransparent")
        sh.inputs[0].default_value = (0.92, 0.95, 0.93, 1) if spec.get("glass") else (0.75, 0.75, 0.75, 1)
        nt.links.new(sh.outputs[0], out.inputs[0])
    elif spec.get("unlit"):
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs[1].default_value = spec["unlit"]
        nt.links.new(base, em.inputs[0])
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader")
        nt.links.new(alpha, mx.inputs[0])
        nt.links.new(tr.outputs[0], mx.inputs[1])
        nt.links.new(em.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs[0])
    elif spec.get("emit"):
        sh = nt.nodes.new("ShaderNodeEmission")
        sh.inputs[1].default_value = spec["emit"]
        if base: nt.links.new(base, sh.inputs[0])
        else: sh.inputs[0].default_value = col
        nt.links.new(sh.outputs[0], out.inputs[0])
    else:
        sh = nt.nodes.new("ShaderNodeBsdfPrincipled")
        if base: nt.links.new(base, sh.inputs["Base Color"])
        else: sh.inputs["Base Color"].default_value = col
        sh.inputs["Roughness"].default_value = spec.get("rough", 0.7)
        sh.inputs["Metallic"].default_value = spec.get("metal", 0.0)
        if alpha:
            nt.links.new(alpha, sh.inputs["Alpha"])
        nt.links.new(sh.outputs[0], out.inputs[0])
    if page_img is not None:
        uv1 = nt.nodes.new("ShaderNodeUVMap")
        uv1.uv_map = "uv1"
        bk = nt.nodes.new("ShaderNodeTexImage")
        bk.image = page_img
        bk.name = "BAKE"
        nt.links.new(uv1.outputs[0], bk.inputs[0])
        nt.nodes.active = bk
    return m


def build_scene(sc):
    B = house.build()
    for s_ in B.surfs:
        s_.dens *= SIZE / 2048.0 * 0.8
    pages = B.pack(size=SIZE)
    log("surfaces:", len(B.surfs), "pages:", pages)
    page_imgs = {}
    by_obj = {}
    for s in B.surfs:
        by_obj.setdefault((s.page, getattr(s, "node", None)), {}).setdefault(s.mat, []).append(s)
    hinges = {d["name"]: d["hinge"] for d in B.doors}
    objs = []
    for (page, node), mats in sorted(by_obj.items(), key=lambda kv: (kv[0][0], kv[0][1] or "")):
        if page != "fx" and page not in page_imgs:
            page_imgs[page] = None  # Export/encode need page identity, not empty pixel buffers.
            if opt("--bake"):
                im = bpy.data.images.new("lm_" + page, SIZE, SIZE, alpha=False, float_buffer=True)
                im.colorspace_settings.name = "Non-Color"
                page_imgs[page] = im
        hx, hy = hinges.get(node, (0.0, 0.0))
        verts, faces, uv0, uv1, nrm, midx = [], [], [], [], [], []
        me = bpy.data.meshes.new(("%s__%s" % (node, page)) if node else "page_" + page)
        for mi, (mat, lst) in enumerate(sorted(mats.items())):
            mname = "%s__%s" % (mat, page)
            me.materials.append(bpy.data.materials.get(mname) or make_material(mname, house.MATS[mat], page_imgs.get(page)))
            for s in lst:
                o = len(verts)
                verts += [((v.x - hx) * FT, (v.y - hy) * FT, v.z * FT) for v in s.verts]
                u1 = B.uv1(s)
                for t in s.tris:
                    faces.append((o + t[0], o + t[1], o + t[2]))
                    midx.append(mi)
                    for k in t:
                        uv0.append(s.uv0[k]); uv1.append(u1[k]); nrm.append(tuple(s.nrm[k]))
        me.from_pydata(verts, [], faces)
        for nm, data in (("uv0", uv0), ("uv1", uv1)):
            l = me.uv_layers.new(name=nm)
            l.data.foreach_set("uv", [c for uvp in data for c in uvp])
        me.polygons.foreach_set("material_index", midx)
        me.polygons.foreach_set("use_smooth", [True] * len(faces))
        me.normals_split_custom_set(nrm)
        ob = bpy.data.objects.new(me.name, me)
        ob.location = (hx * FT, hy * FT, 0.0)
        ob["page"] = page
        sc.collection.objects.link(ob)
        if page == "fx":
            ob.visible_shadow = False
            ob.visible_diffuse = False
        objs.append(ob)
    # sky
    w = bpy.data.worlds.new("sky")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    env = nt.nodes.new("ShaderNodeTexEnvironment")
    env.image = bpy.data.images.load(HDRI)
    mp = nt.nodes.new("ShaderNodeMapping")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp.inputs["Rotation"].default_value = (0, 0, SUN_ROT)
    nt.links.new(tc.outputs["Generated"], mp.inputs[0])
    nt.links.new(mp.outputs[0], env.inputs[0])
    nt.links.new(env.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = 1.0
    nt.links.new(bg.outputs[0], out.inputs[0])
    # warm interior fixtures
    for i, (x, y, z, p) in enumerate(B.lights):
        ld = bpy.data.lights.new("L%d" % i, "AREA" if i in B.downlights else "POINT")
        ld.energy = 22.0 * p
        if i in B.downlights:
            # Blender area lights face local -Z: recessed cans cannot shine up onto the ceiling.
            ld.shape = "DISK"
            ld.size = 2 * B.downlights[i] * FT
        # daylight bulbs in the main-floor baths and the kitchen track; soft white elsewhere (owner)
        yd = y                                        # already in measured space
        cool = (z < 8.5 and ((33.3 < x < 46 and 14.4 < yd < 22.9) or (24.1 < x < 29.7 and yd > 21.1) or (11 < x < 24.1 and yd > 16))) \
            or (12 < x < 18 and 18 < yd < 21 and z > 14)        # the kitchen track
        ld.color = (0.95, 0.97, 1.0) if cool else (1.0, 0.86, 0.7)
        if i not in B.downlights:
            ld.shadow_soft_size = 0.08
        lo = bpy.data.objects.new("L%d" % i, ld)
        lo.location = (x * FT, y * FT, z * FT)
        sc.collection.objects.link(lo)
    return B, objs, page_imgs


VIEWS = {
    # name: (eye, target, focal mm) in feet, after listing photographs
    "p02_great":   ((17.5, 13.8, 4.6), (0.5, 13.5, 6.5), 15),
    "p45_north":   ((9.0, 23.0, 4.5), (10.0, 0.5, 6.5), 15),
    "p46_west":    ((3.0, 9.5, 4.8), (24.0, 17.5, 6.0), 15),
    "p15_kitchen": ((14.0, 19.0, 4.8), (24.0, 25.0, 4.2), 16),
    "p49_hall":    ((31.5, 14.8, 5.0), (20.0, 19.0, 4.5), 15),
    "p18_bed":     ((32.5, 12.5, 4.8), (44.0, 2.0, 3.5), 15),
    "p37_bed":     ((44.5, 1.5, 4.8), (33.0, 14.0, 4.0), 15),
    "p55_bath":    ((36.5, 18.0, 5.0), (45.5, 19.5, 3.0), 15),
    "p56_bath":    ((44.5, 17.6, 5.0), (33.5, 17.0, 3.5), 15),
    "p54_mud":     ((44.5, 25.2, 5.0), (30.0, 25.0, 4.0), 15),
    "p21_loft":    ((43.5, 12.0, 13.9), (22.0, 16.0, 12.6), 15),
    "p22_loft_w":  ((27.0, 15.0, 13.9), (45.7, 9.0, 12.6), 15),
    "p23_bedroom": ((50.0, 19.5, 13.9), (66.0, 7.0, 12.5), 15),
    "p24_bath":    ((28.5, 17.5, 14.0), (21.5, 26.0, 12.5), 15),
    "p12_down":    ((21.5, 17.5, 14.5), (2.0, 12.0, 3.0), 13),
    "p01_hero":    ((-32.0, -42.0, 3.0), (26.0, 4.0, 9.0), 26),
    "p40_front":   ((22.2, -36.0, 3.2), (22.2, 0.0, 8.0), 28),
    "p41_east":    ((-48.0, 16.0, -6.0), (0.0, 13.0, 8.0), 22),
    "p16_deck":    ((-7.5, 3.0, 5.0), (-1.0, 16.0, 6.0), 15),
    "p50_porch":   ((36.0, 31.2, 5.0), (2.0, 31.0, 3.5), 15),
    "plan":        ((34.0, 14.0, 95.0), (34.0, 14.01, 0.0), 30),
}


# Plan frame of the listing's 3D tour (metres, origin mid-house) -> model feet.
TOUR_X0, TOUR_Y0 = 28.8, 17.7
TOUR_BOUNDS = {  # floor id: (xmin, xmax, ymin, ymax, floor z in feet), from each floor plan's meta block
    "9870264d1b": (-12.327500343322754, 12.551201820373535, -5.9531450271606445, 5.259100914001465, 0.0),
    "663f533dbb": (-11.92710018157959, 8.782702445983887, -3.577000141143799, 4.263899803161621, 9.1),
}
TOUR_UPPER = (40.6 - 28.8, 12.2 - 17.7)   # the upper-floor scan sits offset from the main one (feet)


# Per-photograph corrections found by overlay: id8 -> (dx, dy, dz feet, heading deg, pitch deg)
CAMERA_TUNE = {}
# Poses solved by hand from known floor points, taking precedence over the automatic fit.
MANUAL_TUNE = {"4fb1f0b7": (0.0, 0.0, -0.6, -0.5, 0.5, 0.0, 0.03)}


def tour_cameras(path, height=4.6):
    """Listing photographs with the pose Zillow's tour assigns them: {id: (eye, heading deg, hfov deg)}."""
    cal = json.load(open(path))
    cams = {}
    for pid, floor, px, py, ang, fov in cal["photoLoc"]:
        if floor not in TOUR_BOUNDS:
            continue
        x0, x1, y0, y1, fz = TOUR_BOUNDS[floor]
        X = (x0 + px / 100.0 * (x1 - x0)) / FT + TOUR_X0
        Y = (y1 - py / 100.0 * (y1 - y0)) / FT + TOUR_Y0
        if fz:                                            # same fit as plan_extract.py
            X = (X - TOUR_X0) * 69.1 / 67.2 + 0.5 + 38.8 * 69.1 / 67.2
            Y = Y - TOUR_Y0 + 13.3
        cams[pid] = ((X, Y, fz + height), ang, fov)
    return cams


if opt("--cal", ""):
    for pid, (eye, ang, fov) in tour_cameras(opt("--cal", "")).items():
        a = math.radians(ang)
        tgt = (eye[0] + 10 * math.sin(a), eye[1] + 10 * math.cos(a), eye[2])
        VIEWS["z_" + pid[:8]] = (eye, tgt, 18.0 / math.tan(math.radians(fov) / 2))


def render_views(sc, names, out, samples=48, res=(1100, 733)):
    sc.cycles.samples = samples
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.view_settings.view_transform = "AgX"
    sc.view_settings.look = "AgX - Medium High Contrast"
    os.makedirs(out, exist_ok=True)
    cd = bpy.data.cameras.new("cam")
    co = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(co)
    sc.camera = co
    cd.sensor_width = 36
    cd.clip_start, cd.clip_end = 0.05, 2000
    for n in names:
        eye, tgt, f = VIEWS[n]
        e, t = Vector(eye) * FT, Vector(tgt) * FT
        co.location = e
        co.rotation_euler = (t - e).to_track_quat("-Z", "Y").to_euler()
        cd.lens = f
        interior = 0.5 < eye[0] < 70 and 0.5 < eye[1] < 27 and eye[2] < 30
        sc.view_settings.exposure = 1.6 if interior else -0.6
        sc.render.filepath = os.path.join(out, n + ".jpg")
        sc.render.image_settings.file_format = "JPEG"
        bpy.ops.render.render(write_still=True)
        log("rendered", n)


def bake(sc, objs, page_imgs):
    sc.cycles.samples = SAMPLES
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 8
    sc.cycles.diffuse_bounces = 6
    sc.cycles.sample_clamp_indirect = 8.0
    bk = sc.render.bake
    bk.use_pass_direct = bk.use_pass_indirect = True
    bk.use_pass_color = False
    bk.margin = 4
    bk.margin_type = "EXTEND"
    bk.use_clear = True
    bk.use_clear = False                      # several objects share one atlas page
    only = opt("--pages", "").split(",") if opt("--pages", "") else None
    for page in sorted(page_imgs):
        if only and page not in only:
            continue
        sel = [o for o in objs if o["page"] == page]
        bpy.ops.object.select_all(action="DESELECT")
        for ob in sel:
            ob.select_set(True)
            for sl in ob.material_slots:
                nt = sl.material.node_tree
                nt.nodes.active = nt.nodes["BAKE"]
            ob.data.uv_layers.active = ob.data.uv_layers["uv1"]
        bpy.context.view_layer.objects.active = sel[0]
        log("baking", page, len(sel), "objects")
        bpy.ops.object.bake(type="DIFFUSE")
        for ob in sel:
            ob.data.uv_layers.active = ob.data.uv_layers["uv0"]
        im = page_imgs[page]
        im.filepath_raw = os.path.join(WORK, "lm_%s.exr" % page)
        im.file_format = "OPEN_EXR"
        im.save()
        log("saved", im.filepath_raw)
        import subprocess
        subprocess.run([bpy.app.binary_path, "-b", "--factory-startup", "-P", os.path.join(HERE, "denoise.py"), "--",
                        im.filepath_raw, os.path.join(WORK, "lm_%s_dn.exr" % page)], check=True, capture_output=True)
        log("denoised", page)


def encode(page_imgs, B):
    """EXR irradiance -> 8-bit lightmaps. Stored value = (L * gain / RANGE) ** (1 / 2.2)."""
    out = os.path.join(WORK, "out")
    os.makedirs(out, exist_ok=True)
    signature = layout_signature(B)
    sig_path = os.path.join(WORK, "lm_sig.txt")
    if not os.path.exists(sig_path) or open(sig_path).read() != signature:
        raise ValueError("Geometry or lighting changed: run a full --bake before --encode")
    gains, data = {}, {}
    for page in sorted(page_imgs):
        p = os.path.join(WORK, "lm_%s_dn.exr" % page)
        if not os.path.exists(p):
            p = os.path.join(WORK, "lm_%s.exr" % page)
        if not os.path.exists(p):
            raise FileNotFoundError(p)
        im = bpy.data.images.load(p)
        w, h = im.size
        a = np.empty(w * h * 4, dtype=np.float32)
        im.pixels.foreach_get(a)
        a = np.maximum(a.reshape(h, w, 4)[:, :, :3], 0)
        # Every surface edge is also the edge of its lightmap island, where texels are only
        # partly covered and the denoiser has blurred in the black between islands. Left
        # alone that shows as a dark seam along every wall, ceiling and floor edge. So the
        # outermost ring of each island is discarded and regrown outward from its interior.
        raw_path = os.path.join(WORK, "lm_%s.exr" % page)
        if os.path.exists(raw_path):
            ri = bpy.data.images.load(raw_path)
            r = np.empty(w * h * 4, dtype=np.float32)
            ri.pixels.foreach_get(r)
            valid = r.reshape(h, w, 4)[:, :, :3].sum(axis=2) > 1e-5
            bpy.data.images.remove(ri)
        else:
            valid = a.sum(axis=2) > 1e-5
        inner = valid.copy()
        for ax, sh in ((0, 1), (0, -1), (1, 1), (1, -1)):
            inner &= np.roll(valid, sh, axis=ax)
        filled = inner.copy()
        out_ = np.where(filled[..., None], a, 0)
        for _ in range(12):
            acc = np.zeros_like(out_); cnt = np.zeros((h, w), dtype=np.float32)
            for ax, sh in ((0, 1), (0, -1), (1, 1), (1, -1)):
                acc += np.roll(out_, sh, axis=ax); cnt += np.roll(filled, sh, axis=ax)
            grow = (~filled) & (cnt > 0)
            out_[grow] = acc[grow] / cnt[grow][:, None]
            filled |= grow
        # islands too thin to have an interior keep what they had
        keep = valid & ~filled
        out_[keep] = a[keep]
        data[page] = out_
    lumw = np.array([0.2126, 0.7152, 0.0722], dtype=np.float32)
    # one exposure for all interior pages and one for all exterior pages
    for prefix, target, pct in (("in", 0.52, 55), ("ex", 1.05, 95)):
        lit = np.concatenate([(d @ lumw)[(d @ lumw) > 1e-4].ravel() for pg, d in data.items() if pg.startswith(prefix)] or [np.ones(1)])
        g = float(target / np.percentile(lit, pct))
        log("exposure", prefix, "gain %.3f" % g, "p50 %.4f p99 %.4f" % (np.percentile(lit, 50), np.percentile(lit, 99)))
        for pg in data:
            if pg.startswith(prefix):
                gains[pg] = g
    for page, a in data.items():
        h, w = a.shape[:2]
        enc = np.clip(a * gains[page] / LM_RANGE, 0, 1) ** (1 / 2.2)
        o = bpy.data.images.new("enc_" + page, w, h, alpha=False)
        o.colorspace_settings.name = "Non-Color"
        px = np.ones((h, w, 4), dtype=np.float32)
        px[:, :, :3] = enc
        o.pixels.foreach_set(px.ravel())
        o.filepath_raw = os.path.join(out, "lm_%s.png" % page)
        o.file_format = "PNG"
        o.save()
    json.dump({"range": LM_RANGE, "gains": gains, "signature": signature}, open(os.path.join(out, "lightmaps.json"), "w"))


def layout_signature(B):
    """Fingerprint bake inputs, not just atlas rectangles (moving a wall keeps its rectangle)."""
    import hashlib
    from pathlib import Path
    h = hashlib.sha256()
    def add(value):
        h.update(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())
    add([SIZE, SAMPLES, SUN_ROT, LM_RANGE, house.MATS, B.lights, B.downlights])
    for s in B.surfs:
        add([s.mat, s.page, s.ox, s.oy, s.dens, s.lm, s.tris, s.uv0,
             [tuple(v) for v in s.verts], [tuple(n) for n in s.nrm]])
    # Source changes can alter shader/light settings without changing geometry.
    for path in sorted(Path(HERE).glob("*.py")) + [Path(HDRI)] + sorted(Path(TEX).glob("*")):
        if path.is_file():
            h.update(path.name.encode())
            with path.open("rb") as source:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    h.update(chunk)
    return h.hexdigest()


SEE_THROUGH = {"screen", "canopy", "lampglow", "water", "fire", "lattice"}
OUTDOOR_MATS = {"grass", "leaves", "gravel", "pavers", "bark", "canopy"}
# deliberate ways out of the envelope: the open halves of the two sliders (x0, x1, y0, y1, z1)
WAYS_OUT = [(-0.5, 1.0, 3.4, 10.4, 7.8), (-0.5, 1.0, 17.0, 24.0, 7.8)]


def check_shell(B):
    """Cast rays from inside every room. A ray that leaves the house envelope without
    passing glass or a deliberate opening is a hole; a first hit on the back of a
    surface means a face is missing on the side one can actually stand on."""
    from mathutils import Vector
    from mathutils.bvhtree import BVHTree
    import planshell
    verts, tris, owner = [], [], []
    for s in B.surfs:
        if s.mat in SEE_THROUGH or s.mat in OUTDOOR_MATS:
            continue
        o = len(verts)
        verts += [tuple(v) for v in s.verts]
        for a, b, c in s.tris:
            tris.append((o + a, o + b, o + c))
            owner.append(s)
    bvh = BVHTree.FromPolygons(verts, tris)
    dirs = []
    n = 96
    for i in range(n):
        z = 1 - 2 * (i + 0.5) / n
        r = math.sqrt(1 - z * z)
        a = i * math.pi * (3 - math.sqrt(5))
        dirs.append(Vector((r * math.cos(a), r * math.sin(a), z)))
    holes, backs, rays = [], {}, 0
    for room in planshell.PLAN["rooms"]:
        name, poly = room["name"], room["poly"]
        if name in planshell.OUTDOORS or name in ("Garage", "Open To Below") or (room["floor"] == "upper" and name == "Stairs"):
            continue
        z = (house.F2 if room["floor"] == "upper" else 0.0) + 4.5
        xs, ys = [p[0] for p in poly], [p[1] for p in poly]
        step = 3.0
        gx = [min(xs) + 0.8 + step * i for i in range(int((max(xs) - min(xs) - 1.6) / step) + 1)]
        gy = [min(ys) + 0.8 + step * j for j in range(int((max(ys) - min(ys) - 1.6) / step) + 1)]
        for x in gx:
            for y in gy:
                if not planshell.in_poly(x, y, poly):
                    continue
                o = Vector((x, y, z))
                if bvh.find_nearest(o)[3] < 0.25:
                    continue                              # inside a cabinet or a piece of furniture
                for d in dirs:
                    rays += 1
                    loc, nrm, idx, dist = bvh.ray_cast(o, d, 400.0)
                    out = None
                    if loc is None:
                        out = o + d * 60.0
                    else:
                        s = owner[idx]
                        if not (-0.3 < loc.x < 70.3 and -0.3 < loc.y < 27.7) and s.mat != "glass":
                            out = loc
                        elif nrm.dot(d) > 0.05 and s.mat not in ("glass", "mirror"):
                            backs[s.mat] = backs.get(s.mat, 0) + 1
                    if out is not None:
                        # where the ray crossed the envelope
                        ts = []
                        for lo, hi, c0, dc in ((-0.3, 70.3, o.x, d.x), (-0.3, 27.7, o.y, d.y)):
                            if abs(dc) > 1e-9:
                                ts += [t for t in ((lo - c0) / dc, (hi - c0) / dc) if t > 0]
                        t = min(ts) if ts else 0.0
                        e = o + d * t
                        if any(x0 < e.x < x1 and y0 < e.y < y1 and e.z < z1 for x0, x1, y0, y1, z1 in WAYS_OUT):
                            continue
                        holes.append((name or "unnamed", round(x, 1), round(y, 1), round(z, 1), round(e.x, 1), round(e.y, 1), round(e.z, 1)))
    for floor, z in (("main", 1.0), ("upper", house.F2 + 1.0)):
        x = 0.6
        while x < 69.6:
            y = 0.7
            while y < 27.0:
                on_floor = floor == "main" or (x > 20.5 and not (x < 24.2 and y < 13.2))
                if on_floor:
                    if floor == "upper" and (planshell.is_open(x, y)):
                        y += 0.31
                        continue
                    rays += 1
                    loc = bvh.ray_cast(Vector((x, y, z)), Vector((0, 0, -1)), 3.0)[0]
                    if loc is None:
                        holes.append(("floor slot (%s)" % floor, round(x, 1), round(y, 1), z, round(x, 1), round(y, 1), z - 3))
                y += 0.31
            x += 0.31
    by_room = {}
    for h in holes:
        by_room[h[0]] = by_room.get(h[0], 0) + 1
    log("shell check: %d rays, %d escaped, %d first hits on a back face" % (rays, len(holes), sum(backs.values())))
    for k, v in sorted(by_room.items(), key=lambda kv: -kv[1])[:12]:
        log("   escapes from %-24s %d" % (k, v))
    for k, v in sorted(backs.items(), key=lambda kv: -kv[1])[:12]:
        log("   back faces of %-22s %d" % (k, v))
    return {"rays": rays, "escaped": len(holes), "backfaces": sum(backs.values()), "examples": holes[:60], "backface_mats": backs}


def export(sc, B, objs, page_imgs):
    out = os.path.join(WORK, "out")
    os.makedirs(out, exist_ok=True)
    # strip materials down to names; the viewer rebuilds them from scene.json
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=os.path.join(out, "house.glb"), export_format="GLB", use_selection=True,
                              export_materials="EXPORT", export_image_format="NONE",export_normals=True, export_texcoords=True,
                              export_yup=True, export_apply=False, export_cameras=False, export_lights=False,
                              export_draco_mesh_compression_enable=True, export_draco_mesh_compression_level=6,
                              export_draco_position_quantization=14, export_draco_normal_quantization=10,
                              export_draco_texcoord_quantization=14)
    # terrain height grid for walking outdoors
    gx0, gy0, gs, gn = -170.0, -190.0, 4.0, 110
    grid = [round(house.ground(gx0 + i * gs, gy0 + j * gs) * FT, 3) for j in range(gn) for i in range(gn)]
    m = lambda v: round(v * FT, 4)
    floors = []
    for f in B.floors:
        d = {"poly": [[m(x), m(y)] for x, y in f["poly"]]}
        if "ramp" in f:
            y0, z0, y1, z1 = f["ramp"]
            d["ramp"] = [m(y0), m(z0), m(y1), m(z1)]
        else:
            d["z"] = m(f["z"])
        floors.append(d)
    lm_path = os.path.join(out, "lightmaps.json")
    encoded = {}
    if os.path.exists(lm_path):
        with open(lm_path) as f:
            encoded = json.load(f)
    signature = layout_signature(B)
    baked = encoded.get("signature") == signature and all(
        os.path.exists(os.path.join(out, "lm_%s.png" % page)) for page in page_imgs)
    data = {
        "units": "metres; x = west, y = south, z = up (glTF: x, z, -y)",
        "materials": house.MATS,
        "pages": sorted(page_imgs.keys()),
        "solids": [[m(v) for v in s] for s in B.solids],
        "doors": [dict(name=d["name"], hinge=[m(v) for v in d["hinge"]], open=round(d["open"], 4),
                       seg=[m(v) for v in d["seg"]], z0=m(d["z0"]), z1=m(d["z1"])) for d in B.doors],
        "floors": floors,
        "terrain": {"x0": m(gx0), "y0": m(gy0), "step": m(gs), "n": gn, "h": grid},
        "spawn": {"pos": [m(22.4), m(-22.0), m(house.GROUND_N)], "yaw_deg": 0},
        "sun_rot": SUN_ROT,
        "build": int(time.time()),
        "baked": baked,
        "checks": check_shell(B),
        "photoPages": PHOTO_PAGES,  # only projections generated for this exact scene
    }
    with open(os.path.join(out, "scene.json"), "w") as f:
        json.dump(data, f, separators=(",", ":"))
    log("exported", out)


sc = reset()
B, objs, page_imgs = build_scene(sc)
log("scene built; tris:", sum(len(o.data.polygons) for o in objs))
if opt("--preview"):
    names = opt("--views", ",".join(VIEWS)).split(",")
    render_views(sc, names, os.path.join(WORK, "preview"), samples=int(opt("--psamples", "48")))
if opt("--bake"):
    # A failed or partial bake must not leave a previous full-bake stamp valid.
    sig_path = os.path.join(WORK, "lm_sig.txt")
    if os.path.exists(sig_path):
        os.unlink(sig_path)
    bake(sc, objs, page_imgs)
    if not opt("--pages", ""):
        open(os.path.join(WORK, "lm_sig.txt"), "w").write(layout_signature(B))
if opt("--encode"):
    encode(page_imgs, B)
PHOTO_PAGES = []


def photo_zone(P):
    """Where photographs may land (P in measured feet). Left out: the great room above
    door-head height, where the chandelier and fans hang in front of the walls and get
    painted onto them, and the stair, whose balusters do the same to the wall behind."""
    x, y, z = P[..., 0], P[..., 1], P[..., 2]
    great_upper = (x < house.SX0 + 0.3) & (z > 7.6)
    stair = (x > house.SX0 - 0.3) & (x < house.SWX + 0.3) & (y < 13.8)
    return ~(great_upper | stair)


TUNE_FILE = os.path.join(WORK, "camera_fit.json")
if opt("--refine") or opt("--project"):
    import project
    importlib.reload(project)
    only = opt("--only", "").split(",") if opt("--only", "") else None
if opt("--refine"):
    fit = json.load(open(TUNE_FILE)) if os.path.exists(TUNE_FILE) and only else {}
    fit.update(project.refine(B, tour_cameras(opt("--cal", "")), opt("--photos", ""), log=log, only=only,
                              debug_dir=os.path.join(WORK, "fit") if opt("--debug") else None))
    json.dump(fit, open(TUNE_FILE, "w"), indent=1)
    log("fitted %d cameras -> %s" % (len(fit), TUNE_FILE))
if opt("--project"):
    if os.path.exists(TUNE_FILE):
        # a fit that ran into its limits has usually locked onto furniture, not structure
        lim = project.BOUNDS * 0.97
        CAMERA_TUNE.update({k: v for k, v in json.load(open(TUNE_FILE)).items()
                            if abs(v[0]) < lim[0] and abs(v[1]) < lim[1] and abs(v[6]) < lim[6]})
    CAMERA_TUNE.update(MANUAL_TUNE)
    PHOTO_PAGES = project.project(B, tour_cameras(opt("--cal", "")), opt("--photos", ""), os.path.join(WORK, "out"), SIZE,
                                  house.ycal, log=log, only=only, tune=CAMERA_TUNE, keep=photo_zone)
if opt("--export"):
    export(sc, B, objs, page_imgs)
if opt("--save"):
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(WORK, "house.blend"))
log("done")
