"""Run: blender -b -P tests/test_walkthrough_blender.py (tiny synthetic bake; no downloads)."""
import sys
from pathlib import Path
import tempfile
import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts/walkthrough'))
import hb
import house
import project

for drawn in (False, True):
    B = hb.Builder()
    B.mats = house.MATS
    B.poly('paint', [(0, 26.91, 0), (4, 26.91, 0), (4, 26.91, 4), (0, 26.91, 4)])
    surface = B.surfs[0]
    if drawn:
        surface.verts0 = [v.copy() for v in surface.verts]
        for v in surface.verts:
            v.y = house.ycal(v.y)
    B.pack(size=128)
    points = []
    def keep(p):
        points.append(p.copy())
        return np.ones(p.shape[:2], dtype=bool)
    with tempfile.TemporaryDirectory() as tmp:
        project.project(B, {}, tmp, tmp, 128, house.ycal, keep=keep)
    assert points, 'projection must sample test surface'
    expected = house.ycal(26.91) if drawn else 26.91
    assert np.allclose(points[0][..., 1], expected), (drawn, points[0][0, 0, 1], expected)
print('PASS: projection calibrates drawn surfaces once and leaves measured shell unchanged')

# A subpixel south-eave slot used to expose the back of exterior siding.
from mathutils import Vector
from mathutils.bvhtree import BVHTree
B = house.build()
verts, tris, owners = [], [], []
for s in B.surfs:
    offset = len(verts)
    verts.extend(s.verts)
    for t in s.tris:
        tris.append(tuple(offset + k for k in t))
        owners.append(s)
bvh = BVHTree.FromPolygons(verts, tris)
eye = Vector((3, 9.5, 4.8))
direction = (Vector((20.2958279, 27.4, 10.3370438)) - eye).normalized()
hit, normal, index, distance = bvh.ray_cast(eye, direction)
assert hit is not None and owners[index].mat == 'ceiling', 'south-eave join exposes exterior siding'
assert normal.dot(direction) < 0, 'interior must see front of ceiling'
print('PASS: south-eave join is covered by interior ceiling')

B = hb.Builder()
B.mats = house.MATS
house.can_light(B, 2, 3, 8, r=.25)
assert getattr(B, 'downlights', {}) == {0: .25}, 'recessed light must retain aperture radius'
assert abs(B.lights[0][2] - 7.97) < 1e-6, 'recessed source must sit just below aperture'
house.calibrate(B)
assert B.downlights == {0: .25} and abs(B.lights[0][1] - house.ycal(3)) < 1e-6
print('PASS: recessed source stays at aperture through plan calibration')

# Encoding changes brightness only: colored surfaces are not a white-balance reference.
import ast, json, os, bpy
source = Path(house.__file__).with_name('build.py')
tree = ast.parse(source.read_text())
tree.body = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'encode']
with tempfile.TemporaryDirectory() as tmp:
    Path(tmp, 'lm_sig.txt').write_text('test')
    rgb = np.array([.4, .3, .2], dtype=np.float32)
    image = bpy.data.images.new('constant irradiance', 32, 32, alpha=False, float_buffer=True)
    image.colorspace_settings.name = 'Non-Color'
    pixels = np.ones((32, 32, 4), dtype=np.float32)
    pixels[..., :3] = rgb
    image.pixels.foreach_set(pixels.ravel())
    image.file_format = 'OPEN_EXR'
    for suffix in ('.exr', '_dn.exr'):
        image.filepath_raw = str(Path(tmp, 'lm_in0' + suffix))
        image.save()
    ctx = dict(bpy=bpy, np=np, os=os, json=json, WORK=tmp, LM_RANGE=4,
               layout_signature=lambda b: 'test', log=lambda *a: None)
    exec(compile(tree, str(source), 'exec'), ctx)
    ctx['encode']({'in0': image}, None)
    encoded = bpy.data.images.load(str(Path(tmp, 'out/lm_in0.png')))
    encoded.colorspace_settings.name = 'Non-Color'
    values = np.array(encoded.pixels[:]).reshape(32, 32, 4)[16, 16, :3] ** 2.2
    assert np.allclose(values / values[1], rgb / rgb[1], atol=.025), 'encoder introduces scene-average color cast'
print('PASS: lightmap encoding preserves irradiance channel ratios')

# Export retains page/UV identity without allocating bake targets; bake still works.
from types import SimpleNamespace
import time
functions = ast.parse(source.read_text())
functions.body = [n for n in functions.body if isinstance(n, ast.FunctionDef) and n.name in
                  {'image', 'make_material', 'build_scene', 'bake', 'encode', 'export', 'layout_signature'}]

def tiny_house():
    model = hb.Builder()
    model.mats = {'paint': {'color': [.8, .8, .8]}}
    model.poly('paint', [(0, 0, 0), (4, 0, 0), (4, 4, 0), (0, 4, 0)], dens=256)
    return model

with tempfile.TemporaryDirectory(prefix='colonial-tiny-bake-') as tmp:
    sky = bpy.data.images.new('test sky', 8, 4, float_buffer=True)
    sky.pixels[:] = [.5, .5, .5, 1] * 32
    sky.file_format = 'HDR'
    sky.filepath_raw = str(Path(tmp, 'sky.hdr'))
    sky.save()
    options = set()
    Path(tmp, 'textures').mkdir()
    ctx = dict(bpy=bpy, np=np, os=os, json=json, time=time, WORK=tmp, TEX=str(Path(tmp, 'textures')),
               HDRI=str(Path(tmp, 'sky.hdr')), HERE=str(source.parent), SIZE=64, SAMPLES=1,
               SUN_ROT=0, LM_RANGE=4, FT=.3048, PHOTO_PAGES=[],
               house=SimpleNamespace(build=tiny_house, MATS={'paint': {'color': [.8, .8, .8]}},
                                     ground=lambda x, y: 0, GROUND_N=0),
               opt=lambda key, default=None: key in options if default is None else default,
               check_shell=lambda model: {}, log=lambda *a: None)
    exec(compile(functions, str(source), 'exec'), ctx)
    def build():
        bpy.ops.wm.read_factory_settings(use_empty=True)
        sc = bpy.context.scene
        sc.render.engine = 'CYCLES'
        sc.cycles.device = 'CPU'
        sc.render.threads_mode = 'FIXED'
        sc.render.threads = 2
        model, objects, pages = ctx['build_scene'](sc)
        return sc, model, objects, pages
    def identity(objects):
        return [(o.name, o['page'], list(o.location), [list(v.co) for v in o.data.vertices],
                 [list(p.vertices) for p in o.data.polygons],
                 [[list(v.uv) for v in layer.data] for layer in o.data.uv_layers],
                 [m.name for m in o.data.materials]) for o in objects]
    sc, model, objects, pages = build()
    assert pages and all(image is None for image in pages.values()), 'export-only allocated atlas pixels'
    assert not any(i.name.startswith('lm_') for i in bpy.data.images)
    assert not any(m.node_tree.nodes.get('BAKE') for m in bpy.data.materials if m.use_nodes)
    geometry = identity(objects)
    signature = ctx['layout_signature'](model)
    ctx['export'](sc, model, objects, pages)
    unbaked = json.loads(Path(tmp, 'out/scene.json').read_text())
    assert unbaked['pages'] == sorted(pages) and unbaked['baked'] is False
    options.add('--bake')
    sc, model, objects, pages = build()
    assert all(tuple(image.size) == (64, 64) for image in pages.values())
    assert identity(objects) == geometry, 'bake allocation changed geometry/UV/material identity'
    assert ctx['layout_signature'](model) == signature, 'allocation mode changed input signature'
    for obj in objects:
        for slot in obj.material_slots:
            assert slot.material.node_tree.nodes.active.name == 'BAKE'
    ctx['bake'](sc, objects, pages)
    for image in pages.values():
        pixels = np.array(image.pixels[:])
        assert np.isfinite(pixels).all() and pixels.reshape(-1, 4)[:, :3].max() > 0
    Path(tmp, 'lm_sig.txt').write_text(signature)
    ctx['encode'](pages, model)
    # A fresh export-only scene must accept matching maps without recreating targets.
    options.clear()
    sc, model, objects, pages = build()
    assert all(image is None for image in pages.values())
    def exported():
        ctx['export'](sc, model, objects, pages)
        return json.loads(Path(tmp, 'out/scene.json').read_text())['baked']
    assert exported() is True
    vertex = model.surfs[0].verts[0]
    vertex.x += .25
    assert exported() is False, 'geometry change accepted stale bake'
    try:
        ctx['encode'](pages, model)
        raise AssertionError('stale encode accepted')
    except ValueError as error:
        assert 'full --bake' in str(error)
    vertex.x -= .25
    assert exported() is True
    Path(tmp, 'out', 'lm_' + next(iter(pages)) + '.png').unlink()
    assert exported() is False, 'missing page accepted as baked'
print('PASS: export-only allocates no targets; tiny real bake/denoise/encode, page/UV identity and stale rejection')
