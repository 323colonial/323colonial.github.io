"""Run: blender -b -P tests/test_walkthrough_blender.py (no renders or downloads)."""
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
