#!/usr/bin/env python3
"""Private display-only night comparison; physical inputs and photo assets untouched.

blender -b --python-exit-code 1 -P scripts/seasons/night_looks.py
"""
import hashlib
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lighting_reference import ROOT, OUT as INPUT, cct_rgb

OUT = INPUT / 'night-looks'
VIEWS = ('21', '22', '57', '59')
OPTIONS = ((2700, 'Physical baseline'), (3000, 'A · subtle cooling'),
           (3250, 'B · medium cooling'), (3500, 'C · stronger cooling'))
RGB_XYZ = ((.4124564, .3575761, .1804375), (.2126729, .7151522, .0721750),
           (.0193339, .1191920, .9503041))
XYZ_RGB = ((3.2404542, -1.5371385, -.4985314), (-.9692660, 1.8760108, .0415560),
           (.0556434, -.2040259, 1.0572252))
BRADFORD = ((.8951, .2664, -.1614), (-.7502, 1.7135, .0367), (.0389, -.0685, 1.0296))
BRADFORD_INVERSE = ((.9869929, -.1470543, .1599627), (.4323053, .5183603, .0492912),
                    (-.0085287, .0400428, .9684867))


def transform(matrix, vector):
    return tuple(sum(a*b for a, b in zip(row, vector)) for row in matrix)


def matrix_product(a, b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(3))
                       for j in range(3)) for i in range(3))


def adaptation(target):
    """Shared chromatic presentation shift; not a source-CCT or camera-WB change."""
    if target == 2700:
        return ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    rgb_cones = matrix_product(BRADFORD, RGB_XYZ)
    source_white = transform(rgb_cones, cct_rgb(2700))
    target_white = transform(rgb_cones, cct_rgb(target))
    gains = tuple(t/s for t, s in zip(target_white, source_white))
    scaled = tuple(tuple(gains[i]*v for v in row) for i, row in enumerate(rgb_cones))
    return matrix_product(matrix_product(XYZ_RGB, BRADFORD_INVERSE), scaled)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run():
    import bpy
    import numpy as np

    source_record = INPUT / 'results.json'
    physical = json.loads(source_record.read_text())
    for path, expected in physical['source_hashes'].items():
        assert digest(ROOT/path) == expected, f'Physical model changed; rerun reference first: {path}'
    inputs = [INPUT/f'{v}-{part}.exr' for v in VIEWS
              for part in ('lamps-2700', '06-daylight')]
    inputs += [INPUT/f'{v}-06-physical.png' for v in VIEWS] + [source_record]
    before = {str(p.relative_to(ROOT)): digest(p) for p in inputs}
    OUT.mkdir(parents=True, exist_ok=True)
    sc = bpy.context.scene
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = physical['view_transform']
    sc.view_settings.exposure = physical['exposure']
    sc.view_settings.gamma = 1
    sc.view_settings.use_white_balance = False
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGBA'
    sc.render.image_settings.color_depth = '16'
    matrices = {k: adaptation(k) for k, label in OPTIONS}
    record = dict(source='2700K physical lamps plus existing winter daylight; no relighting',
                  operation='shared linear-RGB Bradford chromatic adaptation before fixed AgX',
                  labels='appearance reference whites only, not measured perceived Kelvin or camera WB',
                  matrices=matrices, input_sha256=before, script_sha256=digest(Path(__file__)),
                  blender=bpy.app.version_string, exposure=sc.view_settings.exposure,
                  look=sc.view_settings.look, previews={})

    def load(path):
        im = bpy.data.images.load(str(path), check_existing=False)
        w, h = im.size
        data = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
        bpy.data.images.remove(im)
        assert np.isfinite(data).all(), path
        return data

    for view in VIEWS:
        lamps, sky = [load(INPUT/f'{view}-{part}.exr') for part in ('lamps-2700', '06-daylight')]
        assert lamps.shape == sky.shape
        baseline = lamps + sky
        baseline[:, :, 3] = 1
        h, w, _ = baseline.shape
        for target, label in OPTIONS:
            pixels = baseline.copy()
            pixels[:, :, :3] = baseline[:, :, :3] @ np.array(matrices[target], dtype=np.float32).T
            assert np.isfinite(pixels).all()
            name = f'{view}-{target}.png'
            image = bpy.data.images.new(name, w, h, alpha=True, float_buffer=True)
            image.pixels.foreach_set(pixels.ravel())
            image.save_render(str(OUT/name), scene=sc)
            bpy.data.images.remove(image)
            record['previews'][name] = dict(label=label, sha256=digest(OUT/name),
                negative_channel_fraction=float((pixels[:, :, :3] < 0).mean()))
            if target == 2700:
                assert np.array_equal(load(OUT/name), load(INPUT/f'{view}-06-physical.png')), 'baseline display drift'
    for path, expected in before.items():
        assert digest(ROOT/path) == expected, f'Input changed: {path}'

    headings = ''.join(f'<th>{label}<br><small>{k}K-like reference</small></th>' for k, label in OPTIONS)
    rows = ''.join('<tr><th scope="row">'+view+'</th>'+''.join(
        f'<td><a href="{view}-{k}.png"><img src="{view}-{k}.png" alt="View {view}: {label}"></a></td>'
        for k, label in OPTIONS)+'</tr>' for view in VIEWS)
    (OUT/'review.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width"><title>Night warmth options</title>
<style>body{font:16px system-ui;margin:24px;background:#fafafa;color:#222}p{max-width:1100px;line-height:1.5}
table{width:100%;table-layout:fixed;border-collapse:collapse}th{padding:8px}th:first-child{width:32px}
td{padding:2px}img{display:block;width:100%;height:auto}small{font-weight:normal}a{color:#174b87}</style>
<h1>Night appearance — choose warmth, not bulb temperature</h1>
<p>Physical lamps remain 2700K (daylight exceptions 5000K). Each option applies one shared color transform to all four views, before the same AgX display and exposure. No per-view white balance or exposure fitting. No photographs changed.</p>
<p><strong>B is the suggested starting point</strong> for your 3250K-like impression. Labels describe reference-white shifts, not measured room temperature or camera-WB settings. Wood bounce remains; these are not fully neutralized whites. Compare on the same screen. Click any image for full size.</p>
<table><thead><tr><th>View</th>'''+headings+'</tr></thead><tbody>'+rows+'''</tbody></table>
<p>Next: choose A, B, C, baseline, or an in-between strength. Then test all 18 timeline positions, anchor coolest phase near daylight neutrality and keep transitions smooth. Photo 57's separate pink-tint correction remains pending.</p></html>''')
    (OUT/'recipe.json').write_text(json.dumps(record, indent=2)+'\n')
    print('PASS 16 previews; baseline pixels exact; all source inputs unchanged', flush=True)


if __name__ == '__main__':
    run()
