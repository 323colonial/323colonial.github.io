#!/usr/bin/env python3
"""Private, approximate loft lighting reference. Never edits delivered assets.

blender -b --python-exit-code 1 -P scripts/seasons/lighting_reference.py -- --check
blender -b --python-exit-code 1 -P scripts/seasons/lighting_reference.py -- --render
blender -b --python-exit-code 1 -P scripts/seasons/lighting_reference.py -- --timeline
blender -b --python-exit-code 1 -P scripts/seasons/lighting_reference.py -- --areas
blender -b --python-exit-code 1 -P scripts/seasons/lighting_reference.py -- --kitchen
blender -b --python-exit-code 1 -P scripts/seasons/lighting_reference.py -- --interiors
Uses retained local walkthrough inputs; no network, generation or publication.
"""
import datetime as dt
import hashlib
import json
import math
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / '.pi/artifacts/colonial-66v-lighting'
Y = (.2126, .7152, .0722)
TIMELINE = (0, 1, 2, 3, 4, 4.5, 5, 5.5, 6, 6.5, 7, 7.5, 8, 8.5, 9, 9.5, 10, 11)


def luminance(rgb):
    return sum(a * b for a, b in zip(Y, rgb))


def color_ratios(rgb):
    """No chromaticity is defined for a component with no green-channel light."""
    return (float(rgb[0]/rgb[1]), float(rgb[2]/rgb[1])) if rgb[1] > 0 else (None, None)


def cct_rgb(k):
    """Planckian xy approximation -> linear sRGB, normalized to photopic Y=1.

Not an LED spectrum, camera profile, or an inference from photo pixels.
"""
    if not 1667 <= k <= 25000:
        raise ValueError('CCT outside approximation range')
    if k <= 4000:
        x = -.2661239e9 / k**3 - .2343580e6 / k**2 + .8776956e3 / k + .179910
    else:
        x = -3.0258469e9 / k**3 + 2.1070379e6 / k**2 + .2226347e3 / k + .240390
    if k <= 2222:
        y = -1.1063814*x**3 - 1.34811020*x**2 + 2.18555832*x - .20219683
    elif k <= 4000:
        y = -.9549476*x**3 - 1.37418593*x**2 + 2.09137015*x - .16748867
    else:
        y = 3.0817580*x**3 - 5.87338670*x**2 + 3.75112997*x - .37001483
    X, Z = x/y, (1-x-y)/y
    rgb = (3.2406*X - 1.5372 - .4986*Z, -.9689*X + 1.8758 + .0415*Z,
           .0557*X - .2040 + 1.0570*Z)
    return tuple(v/luminance(rgb) for v in rgb)


def spot_fraction(angle):
    """Fraction of a point source's sphere inside a hard-edged spot cone."""
    if not 0 < angle <= math.pi:
        raise ValueError('Spot angle must be in (0, pi]')
    return (1-math.cos(angle/2))/2


def sun_direction(azimuth, elevation):
    az, el = map(math.radians, (azimuth, elevation))
    return (-math.sin(az)*math.cos(el), -math.cos(az)*math.cos(el), math.sin(el))


def interpolate(value, anchors):
    if value <= anchors[0][0]:
        return anchors[0][1]
    for (a, x), (b, y) in zip(anchors, anchors[1:]):
        if value <= b:
            return x + (y-x)*(value-a)/(b-a)
    return anchors[-1][1]


def season(key):
    sys.path.insert(0, str(ROOT / 'scripts/seasons'))
    import pilot
    import light
    # Reuse only pure schedule/solar helpers. No generator entry point is called.
    original = pilot.STEPS[0]
    try:
        pilot.STEPS[0] = (0, '', '', (10, 1, 10, 0), '')
        az, el = pilot.sun(key)
        local = dt.datetime(2026, *pilot.S(key)[3], tzinfo=pilot.TZ)
    finally:
        pilot.STEPS[0] = original
    total = 10**light.loglux(el)
    diffuse_fraction = .3 if el > 10 else .6
    sky = total if el <= 0 else total * diffuse_fraction
    normal = 0 if el <= 0 else (total-sky)/math.sin(math.radians(el))
    # ponytail: no surveyed tree horizon; replace these scalar canopy guesses if calibrated data arrives.
    canopy = interpolate(key, ((0, .3), (3, .5), (6, 1), (9, .6), (12, .3)))
    return dict(key=key, label=pilot.lab(key), local=local.isoformat(), azimuth=az, elevation=el,
                sky_lux_horizontal=sky, sun_lux_normal=normal*canopy,
                direct_canopy_factor=canopy, sky_kelvin=7500 if el > 0 else 9000,
                sun_kelvin=interpolate(el, ((0, 3000), (5, 3500), (12, 4300), (30, 5200), (60, 6000))))


def run(check_only=False, timeline=False, areas=False, kitchen=False, interiors=False):
    import bpy
    import numpy as np
    import runpy
    from mathutils import Vector

    out = OUT/'interiors' if interiors else OUT/'kitchen' if kitchen else OUT/'areas' if areas else OUT/'timeline' if timeline else OUT
    keys = TIMELINE if timeline else (0, 3, 6, 9)
    out.mkdir(parents=True, exist_ok=True)
    work = ROOT / '.pi/artifacts/colonial-vby/work'
    assert (work / 'sky.hdr').is_file() and (work / 'textures').is_dir(), 'retained inputs missing'
    old_argv = sys.argv
    try:
        sys.argv = ['blender', '--', '--work', str(work), '--size', '256']
        ns = runpy.run_path(str(ROOT / 'scripts/walkthrough/build.py'))
    finally:
        sys.argv = old_argv
    sc, B = ns['sc'], ns['B']
    FT = ns['FT']
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 12
    sc.cycles.diffuse_bounces = 8
    sc.cycles.transparent_max_bounces = 16
    sc.cycles.seed = 66
    sc.render.resolution_percentage = 100
    sc.render.resolution_x, sc.render.resolution_y = 640, 426
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = 'AgX - Medium High Contrast'
    sc.view_settings.exposure = 4
    sc.view_settings.gamma = 1
    sc.view_settings.use_white_balance = False
    camera = bpy.data.objects.new('reference_camera', bpy.data.cameras.new('reference_camera'))
    sc.collection.objects.link(camera)
    sc.camera = camera
    camera.data.sensor_width = 36
    camera.data.clip_start = .02
    camera.data.clip_end = 2000

    component_hashes = {}

    def render_array(name):
        sc.render.image_settings.file_format = 'OPEN_EXR'
        sc.render.image_settings.color_depth = '32'
        sc.render.filepath = str(out / (name + '.exr'))
        bpy.ops.render.render(write_still=True)
        rendered = Path(sc.render.filepath)
        component_hashes[rendered.name] = hashlib.sha256(rendered.read_bytes()).hexdigest()
        image = bpy.data.images.load(sc.render.filepath, check_existing=False)
        pixels = np.array(image.pixels[:], dtype=np.float32).reshape(
            sc.render.resolution_y, sc.render.resolution_x, 4)
        bpy.data.images.remove(image)
        assert np.isfinite(pixels).all() and pixels[:, :, :3].max() > 0, name
        return pixels

    def save_display(name, pixels):
        h, w, _ = pixels.shape
        im = bpy.data.images.new(name, w, h, alpha=True, float_buffer=True)
        im.pixels.foreach_set(pixels.ravel())
        sc.render.image_settings.file_format = 'PNG'
        im.save_render(str(out / (name + '.png')), scene=sc)
        bpy.data.images.remove(im)

    def set_source(data, flux, kelvin):
        rgb = cct_rgb(kelvin)
        peak = max(rgb)
        data.color = tuple(v/peak for v in rgb)
        data.energy = flux*peak/683
        if data.type == 'SPOT':
            assert data.spot_blend == 0, 'flux normalization assumes hard cone'
            data.energy /= spot_fraction(data.spot_size)

    # Verify renderer's point-source normalization, independently of house geometry.
    hidden = [(o, o.hide_render) for o in sc.objects if o != camera]
    for o, _ in hidden:
        o.hide_render = True
    sc.world.use_nodes = True
    nt = sc.world.node_tree
    nt.nodes.clear()
    bg = nt.nodes.new('ShaderNodeBackground')
    wo = nt.nodes.new('ShaderNodeOutputWorld')
    nt.links.new(bg.outputs[0], wo.inputs[0])
    bg.inputs['Strength'].default_value = 0
    bpy.ops.mesh.primitive_plane_add(size=4)
    plane = bpy.context.object
    mat = bpy.data.materials.new('calibration_white')
    mat.use_nodes = True
    mn = mat.node_tree
    mn.nodes.clear()
    diffuse = mn.nodes.new('ShaderNodeBsdfDiffuse')
    diffuse.inputs['Color'].default_value = (1, 1, 1, 1)
    mo = mn.nodes.new('ShaderNodeOutputMaterial')
    mn.links.new(diffuse.outputs[0], mo.inputs[0])
    plane.data.materials.append(mat)
    ld = bpy.data.lights.new('calibration_point', 'POINT')
    ld.shadow_soft_size = 0
    lo = bpy.data.objects.new('calibration_point', ld)
    sc.collection.objects.link(lo)
    lo.location = (0, 0, 1)
    camera.location = (0, 0, .5)
    camera.rotation_euler = (0, 0, 0)
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = .04
    sc.render.resolution_x = sc.render.resolution_y = 32
    sc.cycles.use_denoising = False
    calibration = []
    for kind, k in (('POINT', 2700), ('POINT', 5000), ('SPOT', 5000), ('AREA', 5000)):
        ld.type = kind
        ld = bpy.data.lights[ld.name]  # Refresh RNA subtype after changing light type.
        if kind == 'SPOT':
            ld.spot_size, ld.spot_blend = math.radians(45), 0
        elif kind == 'AREA':
            ld.shape, ld.size = 'DISK', .01
        set_source(ld, 683, k)
        a = render_array(f'calibration-{kind}-{k}')
        actual = float(a[8:24, 8:24, :3].mean(axis=(0, 1)) @ np.array(Y))
        expected = 1/(4*math.pi**2)
        if kind == 'SPOT':
            expected /= spot_fraction(ld.spot_size)
        elif kind == 'AREA':
            expected *= 4  # Small one-sided Lambertian disk, viewed on axis.
        calibration.append(dict(type=kind, kelvin=k, actual=actual, expected=expected))
        assert abs(actual/expected-1) < .05, calibration
    # One neutral glazing crossing must attenuate actual light transport by .85.
    ld.type = 'POINT'
    ld = bpy.data.lights[ld.name]
    set_source(ld, 683, 5000)
    bpy.ops.mesh.primitive_plane_add(size=4, location=(0, 0, .75))
    pane = bpy.context.object
    glass = bpy.data.materials.new('calibration_glass')
    glass.use_nodes = True
    gn = glass.node_tree
    gn.nodes.clear()
    transparent = gn.nodes.new('ShaderNodeBsdfTransparent')
    transparent.inputs[0].default_value = (.85, .85, .85, 1)
    go = gn.nodes.new('ShaderNodeOutputMaterial')
    gn.links.new(transparent.outputs[0], go.inputs[0])
    pane.data.materials.append(glass)
    a = render_array('calibration-glazing')
    actual = float(a[8:24, 8:24, :3].mean(axis=(0, 1)) @ np.array(Y))
    expected = .85/(4*math.pi**2)
    assert abs(actual/expected-1) < .05, (actual, expected)
    calibration.append(dict(type='POINT_THROUGH_GLASS', kelvin=5000, actual=actual, expected=expected))
    bpy.data.objects.remove(pane, do_unlink=True)
    bpy.data.objects.remove(plane, do_unlink=True)
    bpy.data.objects.remove(lo, do_unlink=True)
    for o, value in hidden:
        o.hide_render = value
    camera.data.type = 'PERSP'
    sc.cycles.use_denoising = True
    sc.render.resolution_x, sc.render.resolution_y = 640, 426

    # Flat diffuse bounce colors avoid counting photographed illumination twice.
    reflectance = dict(paint=(.84, .82, .78), ceiling=(.84, .83, .80),
                       paint_blue=(.21, .30, .46), paint_salt=(.61, .644, .591),
                       paint_sage=(.638, .571, .480), carpet=(.48, .41, .31),
                       oakfloor=(.36, .23, .12), oak=(.40, .26, .13), trim=(.40, .26, .13),
                       oakdoor=(.40, .26, .13), oakdoors2=(.40, .26, .13))
    for mat in bpy.data.materials:
        base = mat.name.split('__')[0]
        if base not in ns['house'].MATS:
            continue
        nodes = mat.node_tree.nodes
        links = mat.node_tree.links
        output = next(n for n in nodes if n.type == 'OUTPUT_MATERIAL')
        if base in ('glass', 'screen', 'canopy'):
            nodes.clear()
            output = nodes.new('ShaderNodeOutputMaterial')
            tr = nodes.new('ShaderNodeBsdfTransparent')
            transmission = .85 if base == 'glass' else .75 if base == 'screen' else 1
            tr.inputs[0].default_value = (transmission,)*3 + (1,)
            links.new(tr.outputs[0], output.inputs[0])
        elif base in reflectance or ns['house'].MATS[base].get('tex') or any(
                n.type == 'EMISSION' for n in nodes):
            color = reflectance.get(base, ns['house'].MATS[base].get('color', (.35, .30, .24)))
            # Unmeasured textures use a bounded diffuse approximation, not their lit pixels.
            color = tuple(min(.85, v) for v in color)
            sh = nodes.new('ShaderNodeBsdfPrincipled' if base == 'paint_salt' else 'ShaderNodeBsdfDiffuse')
            sh.inputs[0].default_value = color + (1,)
            if base == 'paint_salt':
                sh.inputs['Roughness'].default_value = .3  # Approximate semi-gloss, not measured BRDF.
            if base == 'lattice':
                texture = next(n for n in nodes if n.type == 'TEX_IMAGE' and n.name != 'BAKE')
                tr = nodes.new('ShaderNodeBsdfTransparent')
                mix = nodes.new('ShaderNodeMixShader')
                links.new(texture.outputs['Alpha'], mix.inputs[0])
                links.new(tr.outputs[0], mix.inputs[1])
                links.new(sh.outputs[0], mix.inputs[2])
                links.new(mix.outputs[0], output.inputs[0])
            else:
                links.new(sh.outputs[0], output.inputs[0])
    for ob in sc.objects:
        if ob.type == 'MESH':
            ob.visible_shadow = True
            ob.visible_diffuse = True
    # Lamp-globe geometry is visual only; physical source is the point/disk below it.
    # Keep fx diffuse visibility, including glazing, but disable opaque lamp-globe occlusion.
    for mat in bpy.data.materials:
        if mat.name.split('__')[0] in ('lampglow', 'fire', 'water'):
            nodes = mat.node_tree.nodes
            surface_output = next(n for n in nodes if n.type == 'OUTPUT_MATERIAL')
            tr = nodes.new('ShaderNodeBsdfTransparent')
            mat.node_tree.links.new(tr.outputs[0], surface_output.inputs[0])

    inventory = []
    artificial = []
    for i, (x, y, z, relative) in enumerate(B.lights):
        ob = bpy.data.objects['L' + str(i)]
        flux, kelvin, label = 600, 2700, 'general bulb (approximate)'
        if i in B.downlights:
            flux, label = 700, 'recessed'
        if i in (4, 5, 6):
            flux, kelvin, label = 700, 5000, 'primary bath proxy; actual vanity geometry not modeled'
        if i == 7:
            flux, kelvin, label = 1200, 5000, 'powder two bulbs lumped at existing source'
        if i in (11, 12, 13, 14, 15):
            flux, label = 1200, 'walkway two-bulb approximation'
        if i in (38, 39, 43):
            flux, label = 1800, 'great-room/loft fan three-bulb assumption; four-bulb alternative not tested'
        if i in (42, 45):
            flux, label = 2400, 'bedroom fan four bulbs'
        if i == 37:
            flux, label = 4800, 'chandelier eight-bulb assumption; six-ten count range not tested'
        if interiors and i in (34, 35, 36):
            flux, label = 1050, 'porch approximate 4.5 recessed equivalents across three model positions'
        if i in (16, 17, 18, 19):
            flux, kelvin, label = 600, 5000, 'kitchen directional track; 45-degree assumed beam'
            ob.data.type = 'SPOT'
            ob.data.spot_size = math.radians(45)
            ob.data.spot_blend = 0
            hx = (14.75, 15.32, 15.88, 16.45)[i-16]
            ob.location = Vector((hx+.45*.33, ns['house'].ycal(19.3+.35*.33), 16.9-.42-.82*.33))*FT
            target = ((13, 19, 3), (22, 19, 3), (13, 26, 3), (22, 26, 3))[i-16]
            ob.rotation_euler = (Vector(target)*FT-ob.location).to_track_quat('-Z', 'Y').to_euler()
        set_source(ob.data, flux, kelvin)
        artificial.append((ob, flux, kelvin))
        inventory.append(dict(id=i, label=label, lumens=flux, kelvin=kelvin,
                              position_m=list(ob.location), type=ob.data.type))
    # Sink recessed source is absent from the old model; owner supplies 1400lm.
    ld = bpy.data.lights.new('sink_recessed', 'AREA')
    ld.shape, ld.size = 'DISK', .15
    lo = bpy.data.objects.new('sink_recessed', ld)
    sc.collection.objects.link(lo)
    lo.location = Vector((18.1, 25.9, 8.04))*FT
    artificial.append((lo, 1400, 2700))
    inventory.append(dict(id='sink', label='owner sink LED; approximate position', lumens=1400,
                          kelvin=2700, position_m=list(lo.location), type='AREA'))
    sun = bpy.data.lights.new('season_sun', 'SUN')
    sun.angle = math.radians(.53)
    sun_ob = bpy.data.objects.new('season_sun', sun)
    sc.collection.objects.link(sun_ob)
    sun.energy = 0
    views = {k: ns['VIEWS'][n] for k, n in (('21', 'p21_loft'), ('22', 'p22_loft_w'))}
    views.update({'57': ((32, 15.5, 13.9), (7, 14, 13.5), 18),
                  '59': ((24, 13.8, 14), (0, 13.5, 14), 28)})
    if areas:
        views.update({k: ns['VIEWS'][n] for k, n in (('02', 'p02_great'), ('45', 'p45_north'))})
    if kitchen:
        views = {'kitchen-west': ns['VIEWS']['p15_kitchen'],
                 'kitchen-south': ((19, 20, 4.8), (18.1, 26, 6.2), 18)}
    if interiors:
        views = {k: ns['VIEWS'][n] for k, n in (('18', 'p18_bed'), ('37', 'p37_bed'), ('23', 'p23_bedroom'))}
        views.update({
            '60': ((66, 18, 13.9), (50, 18, 15), 18),
            'powder-a': ((28, 22, 5), (26, 25, 7), 18),
            'powder-b': ((28, 25, 5), (25, 22, 7), 18),
            'bath-a': ((24, 22, 14), (24, 26, 16), 18),
            'bath-b': ((24, 23.4, 14), (24, 18, 16), 18),
            'hall-a': ns['VIEWS']['p49_hall'],
            'hall-b': ((31, 21, 5), (30, 15.5, 7), 18),
            'mud-a': ((44.5, 25.2, 5), (30, 25, 6), 18),
            'mud-b': ((31, 25, 5), (44, 25, 6), 18),
            'porch-a': ((38, 31, 5), (26, 31, 3.5), 28),
            'porch-b': ((10, 31, 5), (22, 31, 3.5), 28),
        })
        # Virtual diffuse cards receive light without altering wood bounce or shadows.
        reflectance['probe'] = (.8, .8, .8)
        probe = bpy.data.materials.new('probe')
        probe.use_nodes = True
        pn = probe.node_tree.nodes
        pn.clear()
        pd = pn.new('ShaderNodeBsdfDiffuse')
        pd.inputs['Color'].default_value = (.8, .8, .8, 1)
        po = pn.new('ShaderNodeOutputMaterial')
        probe.node_tree.links.new(pd.outputs[0], po.inputs[0])
        for x, facing in ((26, 1), (22, -1)):
            for y in (29.8, 31, 32.2):
                bpy.ops.mesh.primitive_plane_add(size=1.2*FT, location=Vector((x, y, 3.5))*FT,
                                                rotation=(0, facing*math.pi/2, 0))
                card = bpy.context.object
                card.data.materials.append(probe)
                card.visible_shadow = False
                card.visible_diffuse = False
                card.visible_glossy = False
    provenance = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in [Path(__file__), ROOT/'scripts/walkthrough/plan.json',
                            ROOT/'scripts/seasons/pilot.py', ROOT/'scripts/seasons/light.py',
                            *sorted((ROOT/'scripts/walkthrough').glob('*.py'))]}
    lattice = next(im for im in bpy.data.images if Path(im.filepath).stem == 'lattice')
    lattice_path = Path(bpy.path.abspath(lattice.filepath))
    report = dict(calibration=calibration, fixtures=inventory, cameras=views,
                  component_sha256=component_hashes,
                  lattice_alpha=dict(path=str(lattice_path), sha256=hashlib.sha256(lattice_path.read_bytes()).hexdigest()),
                  source_hashes=provenance, blender=bpy.app.version_string,
                  seasons=[season(k) for k in keys], reflectance=reflectance,
                  exposure=4, view_transform='AgX - Medium High Contrast', white_balance='fixed linear sRGB / D65; no adaptive WB',
                  limitations=['approximate poses, not photo registration', 'uniform sky; no surveyed trees or weather',
                               'Planckian RGB, not measured LED spectra',
                               'glazing film fixed .85; .80-.90 range not rendered; no calibrated glass BRDF',
                               'lamp/daylight multipliers are sensitivity examples, not full count/glazing uncertainty coverage',
                               'components independently denoised; linear sums are approximate',
                               'peripheral fixtures/texture reflectances approximate; not full-house photometry'], results={})
    (out/'inputs.json').write_text(json.dumps(report, indent=2)+'\n')
    assert len([i for i in inventory if i['label'] == 'recessed' and i['position_m'][2] > 5]) >= 6
    if check_only:
        print('PASS physical math/renderer calibration and source setup', flush=True)
        return

    def pose(view):
        eye, target, lens = views[view]
        camera.location = Vector(eye)*FT
        camera.rotation_euler = (Vector(target)-Vector(eye)).to_track_quat('-Z', 'Y').to_euler()
        camera.data.lens = lens
        bpy.context.view_layer.update()

    def samples_on_paint():
        # Fixed ray-sampled painted patches; reject glass/furniture rather than average whole views.
        corners = camera.data.view_frame(scene=sc)
        xmin, xmax = min(v.x for v in corners), max(v.x for v in corners)
        ymin, ymax = min(v.y for v in corners), max(v.y for v in corners)
        depth = corners[0].z
        w, h = sc.render.resolution_x, sc.render.resolution_y
        rotation = camera.matrix_world.to_3x3()
        deps = bpy.context.evaluated_depsgraph_get()
        coords = {'ceiling': [], 'paint': [], 'probe': []}
        for y in range(4, h, 8):
            for x in range(4, w, 8):
                ray = rotation @ Vector((xmin+(x+.5)/w*(xmax-xmin), ymin+(y+.5)/h*(ymax-ymin), depth))
                hit, loc, normal, face, ob, matrix = sc.ray_cast(deps, camera.location, ray.normalized())
                if hit:
                    material = ob.data.materials[ob.data.polygons[face].material_index].name.split('__')[0]
                    if material in coords:
                        coords[material].append((y, x))
        assert sum(map(len, coords.values())) > 50, coords
        return coords

    def metrics(pixels, coords):
        result = {}
        for material, points in coords.items():
            if not points:
                continue
            a = np.array([pixels[y, x, :3] for y, x in points])
            mean = a.mean(axis=0)
            red_green, blue_green = color_ratios(mean)
            result[material] = dict(samples=len(points), linear_rgb=mean.tolist(),
                                    red_green=red_green, blue_green=blue_green,
                                    luminance=float(mean @ np.array(Y)))
        return result

    for view in views:
        pose(view)
        coords = samples_on_paint()
        (out/f'{view}-sample-pixels.json').write_text(json.dumps(coords))
        lamps = {}
        bg.inputs['Strength'].default_value = 0
        sun.energy = 0
        for kelvin in (2700, 3000):
            for ob, flux, k in artificial:
                set_source(ob.data, flux, kelvin if k == 2700 else k)
            lamps[kelvin] = render_array(f'{view}-lamps-{kelvin}')
        for ob, flux, k in artificial:
            ob.data.energy = 0
        for key in keys:
            s = season(key)
            label = s['label']
            rgb = cct_rgb(s['sky_kelvin'])
            bg.inputs['Color'].default_value = (*rgb, 1)
            bg.inputs['Strength'].default_value = s['sky_lux_horizontal']/(683*math.pi)
            set_source(sun, s['sun_lux_normal'], s['sun_kelvin'])
            sun_ob.rotation_euler = (-Vector(sun_direction(s['azimuth'], s['elevation']))).to_track_quat('-Z', 'Y').to_euler()
            daylight = render_array(f'{view}-{label}-daylight')
            total = lamps[2700]+daylight
            total[:, :, 3] = 1
            save_display(f'{view}-{label}-physical', total)
            # Sensitivity corners, not confidence intervals or Kelvin averages.
            cooler = .8*lamps[3000]+1.5*daylight
            warmer = 1.2*lamps[2700]+.35*daylight
            row = dict(physical=metrics(total, coords), lamps=metrics(lamps[2700], coords),
                       daylight=metrics(daylight, coords), cooler_bound=metrics(cooler, coords),
                       warmer_bound=metrics(warmer, coords))
            assert max(m['luminance'] for m in row['physical'].values()) > 1e-6, f'Unlit/occluded reference camera: {view}'
            if view.startswith('porch-'):
                assert len(coords['probe']) > 50 and row['physical']['probe']['luminance'] > 1e-6, f'Unusable porch probes: {view}'
            for material in row['physical']:
                row['physical'][material]['lamp_fraction_Y'] = row['lamps'][material]['luminance']/row['physical'][material]['luminance']
            report['results'][f'{view}-{label}'] = row
            (out/'results.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS private reference rendered; no delivered assets changed by script', flush=True)


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    if args not in (['--check'], ['--render'], ['--timeline'], ['--areas'], ['--kitchen'], ['--interiors']):
        raise SystemExit('Use Blender with -- --check, --render, --timeline, --areas, --kitchen or --interiors')
    run(check_only=args == ['--check'], timeline=args == ['--timeline'], areas=args == ['--areas'], kitchen=args == ['--kitchen'], interiors=args == ['--interiors'])
