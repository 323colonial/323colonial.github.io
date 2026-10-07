"""Check a real completed bake without changing it.

blender -b --python-exit-code 1 -P tests/verify_walkthrough_lighting.py -- \
    --work /path/to/bake --size 4096 --samples 256
Requires original textures/HDRI, raw and encoded lightmaps, and exported scene.
"""
import argparse
import json
from pathlib import Path
import runpy
import sys
import tempfile

import bpy
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument('--work', required=True, type=Path)
parser.add_argument('--size', type=int, default=4096)
parser.add_argument('--samples', type=int, default=256)
parser.add_argument('--sunrot', type=float, default=77)
args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
work = args.work.resolve()
scene = json.loads((work / 'out/scene.json').read_text())
manifest = json.loads((work / 'out/lightmaps.json').read_text())
assert scene['baked'] is True
assert scene['checks']['escaped'] == 0, scene['checks']
assert set(scene['pages']) == set(manifest['gains'])

# Rebuild the real input geometry, but neither bake nor write into the work directory.
builder = Path(__file__).resolve().parents[1] / 'scripts/walkthrough/build.py'
sys.argv = [str(builder), '--', '--work', str(work), '--size', str(args.size),
            '--samples', str(args.samples), '--sunrot', str(args.sunrot)]
ns = runpy.run_path(str(builder))
B = ns['B']
signature = ns['layout_signature']
base = signature(B)
assert base == manifest['signature'] == (work / 'lm_sig.txt').read_text(), 'stale bake inputs'

stats = {}
for page in scene['pages']:
    images = {}
    for suffix, directory in [('.exr', work), ('_dn.exr', work), ('.png', work / 'out')]:
        path = directory / ('lm_' + page + suffix)
        image = bpy.data.images.load(str(path), check_existing=False)
        assert tuple(image.size) == (args.size, args.size), (path, tuple(image.size))
        # Encoded PNG stores gamma-encoded numerical values, not display imagery.
        image.colorspace_settings.name = 'Non-Color'
        pixels = np.empty(args.size * args.size * 4, dtype=np.float32)
        image.pixels.foreach_get(pixels)
        rgb = pixels.reshape(-1, 4)[:, :3].copy()
        assert np.isfinite(rgb).all() and (rgb >= 0).all(), str(path)
        images[suffix] = rgb
        bpy.data.images.remove(image)
    mask = images['.exr'].sum(axis=1) > 1e-5
    assert mask.any(), 'empty bake: ' + page
    encoded = images['.png'][mask]
    assert encoded.max() <= 1 and encoded.mean() > 0, 'invalid encoded map: ' + page
    stats[page] = {
        'lit_fraction': float(mask.mean()),
        'encoded_lit_mean': float(encoded.mean()),
        'encoded_lit_p95': float(np.percentile(encoded, 95)),
        'encoded_lit_clipped_fraction': float((encoded.max(axis=1) >= 1).mean()),
    }

# Exercise the real exporter against changed geometry and lights. Copies/links and all
# generated GLBs live in a temporary directory; original bake and shipped assets stay intact.
export = ns['export']
globals_ = export.__globals__
original_work = globals_['WORK']
with tempfile.TemporaryDirectory(prefix='colonial-lighting-check-') as tmp:
    out = Path(tmp) / 'out'
    out.mkdir()
    for name in ['lightmaps.json', *['lm_' + p + '.png' for p in scene['pages']]]:
        (out / name).symlink_to(work / 'out' / name)
    globals_['WORK'] = tmp
    def exported_baked():
        export(ns['sc'], B, ns['objs'], ns['page_imgs'])
        return json.loads((out / 'scene.json').read_text())['baked']
    vertex = B.surfs[0].verts[0]
    old_x = vertex.x
    try:
        vertex.x += 0.25
        assert signature(B) != base and exported_baked() is False, 'geometry change kept stale lighting'
    finally:
        vertex.x = old_x
    light = B.lights[0]
    try:
        B.lights[0] = (*light[:3], light[3] * 1.1)
        assert signature(B) != base and exported_baked() is False, 'light change kept stale lighting'
    finally:
        B.lights[0] = light
    assert signature(B) == base and exported_baked() is True, 'matching bake was not restored'
    globals_['WORK'] = original_work

print(json.dumps({'status': 'PASS', 'signature': base, 'pages': stats}, indent=2))
print('PASS: real bake finite/nonempty; matching encoded maps accepted; geometry/light changes rejected')
