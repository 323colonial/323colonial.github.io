#!/usr/bin/env python3
"""Private 18-point appearance reference; no delivered photo changes.

blender -b --python-exit-code 1 -P scripts/seasons/timeline_looks.py
"""
import json
import math
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lighting_reference import ROOT, OUT, TIMELINE, cct_rgb, luminance
from night_looks import (VIEWS, RGB_XYZ, XYZ_RGB, BRADFORD, BRADFORD_INVERSE,
                        matrix_product, transform, adaptation, digest)

RGB_CONES = matrix_product(BRADFORD, RGB_XYZ)
CONES_RGB = matrix_product(XYZ_RGB, BRADFORD_INVERSE)


def white_gains(source, target):
    a, b = transform(RGB_CONES, source), transform(RGB_CONES, target)
    return tuple(y/x for x, y in zip(a, b))


def matrix_from_gains(gains):
    scaled = tuple(tuple(gains[i]*v for v in row) for i, row in enumerate(RGB_CONES))
    return matrix_product(CONES_RGB, scaled)


def treatments(whites, night_index, target):
    if not all(len(w) == 3 and all(math.isfinite(v) and v > 0 for v in w) for w in whites):
        raise ValueError('Illuminant proxies must be positive finite RGB')
    warmth = [math.log(w[0]/w[2]) for w in whites]
    cool = min(range(len(whites)), key=lambda i: warmth[i])
    span = warmth[night_index]-warmth[cool]
    if span <= 1e-8:
        raise ValueError('Night must be warmer than coolest reference')
    weights = [max(0, min(1, (w-warmth[cool])/span)) for w in warmth]
    cool_gains = white_gains(whites[cool], (1, 1, 1))
    night_gains = white_gains(cct_rgb(2700), cct_rgb(target))
    gains = [tuple(a**(1-w)*b**w for a, b in zip(cool_gains, night_gains)) for w in weights]
    return cool, weights, gains


def curve(gains, position):
    """Cyclic C1 interpolation in log-cone gains; position counts two-second segments."""
    p = position % len(gains)
    index = math.floor(p)
    t = p-index
    t = t*t*(3-2*t)
    return tuple(a**(1-t)*b**t for a, b in zip(gains[index], gains[(index+1) % len(gains)]))


def verify_component(path, expected):
    actual = digest(path)
    if actual != expected:
        raise ValueError(f'Physical component changed; rerun reference: {path}')
    return actual


def run():
    import bpy
    import numpy as np
    import subprocess

    source = OUT/'timeline'
    destination = source/'looks'
    record_path = source/'results.json'
    physical = json.loads(record_path.read_text())
    assert [s['key'] for s in physical['seasons']] == list(TIMELINE)
    assert len(physical['results']) == len(TIMELINE)*len(VIEWS), 'incomplete physical render'
    for path, expected in physical['source_hashes'].items():
        assert digest(ROOT/path) == expected, f'Stale physical source: {path}'
    destination.mkdir(parents=True, exist_ok=True)
    whites = []
    reflectance = physical['reflectance']['ceiling']
    for s in physical['seasons']:
        per_view = []
        for view in VIEWS:
            rgb = physical['results'][f"{view}-{s['label']}"]['physical']['ceiling']['linear_rgb']
            proxy = tuple(c/r for c, r in zip(rgb, reflectance))
            per_view.append(tuple(c/luminance(proxy) for c in proxy))
        whites.append(tuple(sum(v[c] for v in per_view)/len(per_view) for c in range(3)))
    night_index = TIMELINE.index(6)
    looks = {name: treatments(whites, night_index, k) for name, k in (('B', 3250), ('C', 3500))}
    coolest = physical['seasons'][looks['B'][0]]
    sc = bpy.context.scene
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = physical['view_transform']
    sc.view_settings.exposure = physical['exposure']
    sc.view_settings.gamma = 1
    sc.view_settings.use_white_balance = False
    report = dict(coolest=coolest, ranking='highest B/R of equal-view normalized ceiling illuminant proxy',
                  illuminant_proxies=whites, physical_record_sha256=digest(record_path),
                  script_sha256=digest(Path(__file__)), shared_math_sha256=digest(ROOT/'scripts/seasons/night_looks.py'),
                  blender=bpy.app.version_string, exposure=sc.view_settings.exposure, look=sc.view_settings.look,
                  interpolation='smoothstep in log-cone gains;18equal2second segments,cyclic',
                  limitations=['rough material/weather model; not measured white balance',
                               'table excluded from reference; pink-table investigation deferred by owner',
                               'static knot images; curve continuity is numerical, not full-motion certification',
                               'no per-view WB or real-photo grade'], inputs={}, outputs={}, auxiliary_outputs={}, treatments={})
    for name, target in (('B', 3250), ('C', 3500)):
        cool, weights, gains = looks[name]
        matrices = [matrix_from_gains(g) for g in gains]
        assert np.allclose(matrices[night_index], adaptation(target), atol=1e-12)
        assert np.allclose(transform(matrices[cool], whites[cool]), (1, 1, 1), atol=1e-6)
        assert curve(gains, 0) == curve(gains, len(TIMELINE))
        report['treatments'][name] = dict(night_target_reference=target, weights=weights,
            knot_gains=gains, knot_matrices=matrices,
            curve_samples=[dict(segment=i/8, gains=curve(gains, i/8)) for i in range(len(TIMELINE)*8+1)])

    def load(path):
        report['inputs'][str(path.relative_to(ROOT))] = verify_component(path, physical['component_sha256'][path.name])
        im = bpy.data.images.load(str(path), check_existing=False)
        w, h = im.size
        pixels = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
        bpy.data.images.remove(im)
        assert np.isfinite(pixels).all()
        return pixels

    for view in VIEWS:
        lamps = load(source/f'{view}-lamps-2700.exr')
        for index, s in enumerate(physical['seasons']):
            daylight = load(source/f"{view}-{s['label']}-daylight.exr")
            assert lamps.shape == daylight.shape
            baseline = lamps+daylight
            baseline[:, :, 3] = 1
            h, w, _ = baseline.shape
            for name in looks:
                pixels = baseline.copy()
                matrix = report['treatments'][name]['knot_matrices'][index]
                pixels[:, :, :3] = baseline[:, :, :3] @ np.array(matrix, dtype=np.float32).T
                assert np.isfinite(pixels).all()
                image = bpy.data.images.new('timeline_display', w, h, alpha=True, float_buffer=True)
                image.pixels.foreach_set(pixels.ravel())
                filename = f"{view}-{s['label']}-{name}.jpg"
                sc.render.image_settings.file_format = 'JPEG'
                sc.render.image_settings.quality = 92
                image.save_render(str(destination/filename), scene=sc)
                if s['key'] == 6:
                    sc.render.image_settings.file_format = 'PNG'
                    sc.render.image_settings.color_mode = 'RGBA'
                    sc.render.image_settings.color_depth = '16'
                    png_name = filename.replace('.jpg', '.png')
                    image.save_render(str(destination/png_name), scene=sc)
                    report['auxiliary_outputs'][png_name] = digest(destination/png_name)
                bpy.data.images.remove(image)
                report['outputs'][filename] = dict(sha256=digest(destination/filename),
                    negative_channel_fraction=float((pixels[:, :, :3] < 0).mean()))
    for path, expected in report['inputs'].items():
        assert digest(ROOT/path) == expected, f'Input changed: {path}'
    assert digest(record_path) == report['physical_record_sha256']
    for name in looks:
        command = ['magick']
        for s in physical['seasons']:
            command += ['(', *[str(destination/f"{v}-{s['label']}-{name}.jpg") for v in VIEWS],
                        '-resize', '160x107!', '+append', ')']
        subprocess.run([*command, '-append', str(destination/f'{name}-overview.jpg')], check=True)
        rows = ''.join('<tr><th scope="row">'+str(s['key'])+'<br><small>'+s['local'][5:16].replace('T',' ')+'</small></th>'+''.join(
            f'<td><a href="{v}-{s["label"]}-{name}.jpg"><img loading="lazy" width="640" height="426" src="{v}-{s["label"]}-{name}.jpg" alt="View {v}, phase {s["key"]}, treatment {name}"></a></td>'
            for v in VIEWS)+'</tr>' for s in physical['seasons'])
        (destination/f'{name}.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>Loft 18-point progression</title><style>body{font:16px system-ui;margin:24px;background:#fafafa;color:#222}p{max-width:1100px;line-height:1.5}table{width:100%;table-layout:fixed;border-collapse:collapse}th{padding:8px}th:first-child{width:105px}td{padding:2px}img{display:block;width:100%;height:auto}small{font-weight:normal}a{color:#174b87}</style>'''+
            f'<h1>18-point loft progression · {name} '+('primary' if name=='B' else 'alternate')+'</h1>'+
            f'<p><a href="B.html">B primary</a> · <a href="C.html">C alternate</a> · <a href="{name}-overview.jpg">All 18 phases overview</a> · <a href="recipe.json">Numerical recipe</a></p>'+
            f'<p>Coolest modeled ceiling-light proxy: phase {coolest["key"]}, {coolest["local"][:16].replace("T"," ")}. That phase is anchored near daylight-neutral (D65). Original Oct1 is not assumed coolest. Same correction per phase across all four views; fixed exposure and AgX. Winter keeps exact selected {name} appearance matrix. Table material unchanged and excluded from white reference.</p>'+
            '<p>Physical lamps remain 2700K/5000K. Rough model, not measured colorimetry; no photographs changed. Rows follow annual timeline, not chronological capture dates. Each segment is 2 seconds; last row returns to 0. Static frames shown; smooth correction curve checked numerically, full motion not certified.</p>'+
            '<table><thead><tr><th>Phase · local time</th>'+''.join(f'<th>View {v}</th>' for v in VIEWS)+'</tr></thead><tbody>'+rows+'</tbody></table></html>')
        for filename in (f'{name}-overview.jpg', f'{name}.html'):
            report['auxiliary_outputs'][filename] = digest(destination/filename)
    (destination/'recipe.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f'PASS 144 appearance previews; coolest phase={coolest["key"]}; exact B/C night endpoints; cyclic curve', flush=True)


if __name__ == '__main__':
    run()
