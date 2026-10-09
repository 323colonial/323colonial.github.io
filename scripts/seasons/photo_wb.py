#!/usr/bin/env python3
"""Private warmth-only photo trials. Run with Blender for its installed NumPy.

blender -b --python-exit-code 1 -P scripts/seasons/photo_wb.py
No originals, seasonal exports or physical model inputs are modified.
"""
import json
import math
from statistics import median
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lighting_reference import ROOT, OUT as MODEL, TIMELINE, luminance
from night_looks import digest

OUT = ROOT/'.pi/artifacts/colonial-66v-photo-wb'
GROUPS = {'loft': ('21', '22', '57', '59'), 'great-room': ('02', '12', '13', '14')}
MODEL_VIEWS = {'loft': ('21', '22', '57', '59'), 'great-room': ('02', '45')}
# Fixed diffuse paint references, x/y/width/height in original delivered dimensions.
PATCHES = {
    '21': ((800, 25, 160, 70), (670, 300, 100, 60), (1050, 50, 140, 70)),
    '22': ((700, 260, 90, 60), (340, 250, 120, 60), (1120, 190, 100, 90)),
    '57': ((170, 150, 180, 130), (500, 250, 120, 100), (1290, 360, 90, 120)),
    '59': ((590, 340, 100, 120), (840, 370, 90, 50), (520, 110, 110, 110)),
    '02': ((540, 20, 140, 100), (95, 150, 100, 70), (1140, 80, 90, 60)),
    '12': ((1100, 110, 100, 70), (150, 80, 90, 60), (560, 190, 140, 45)),
    '13': ((735, 70, 70, 110), (430, 90, 70, 70), (550, 170, 150, 50)),
    '14': ((1130, 420, 100, 110), (1140, 250, 100, 90), (570, 420, 50, 70)),
}


def reference_rgb(patches):
    """Equal-weight per-channel median of three separately sampled paint patches."""
    if len(patches) != 3 or not all(len(p) == 3 and all(math.isfinite(v) and v > 0 for v in p) for p in patches):
        raise ValueError('Three positive finite RGB patch samples required')
    return tuple(median(p[c] for p in patches) for c in range(3))


def warmth_gains(rgb, target):
    """One log-R/B axis; preserve G/sqrt(RB) and mean reference luminance."""
    if len(rgb) != 3 or not all(math.isfinite(v) and v > 0 for v in rgb) or not math.isfinite(target):
        raise ValueError('Positive finite RGB and finite warmth required')
    delta = target-math.log(rgb[0]/rgb[2])
    gains = (math.exp(delta/2), 1., math.exp(-delta/2))
    scale = luminance(rgb)/luminance(tuple(a*b for a, b in zip(rgb, gains)))
    return tuple(v*scale for v in gains)


def photo_shifts(model_shifts):
    """Photographic preview strength; model controls relative room/season variation."""
    peak = max(v[2] for v in model_shifts.values())
    if not math.isfinite(peak) or peak <= 0:
        raise ValueError('Positive modeled night warmth required')
    return {room: [v*math.log(1.10)/peak for v in values] for room, values in model_shifts.items()}


def run():
    import bpy
    import numpy as np
    import subprocess

    OUT.mkdir(parents=True, exist_ok=True)
    source = MODEL/'areas'
    physical = json.loads((source/'results.json').read_text())
    look_path = MODEL/'timeline/looks/recipe.json'
    looks = json.loads(look_path.read_text())
    inputs = {str(p.relative_to(ROOT)): digest(p) for p in (source/'results.json', look_path, Path(__file__), ROOT/'scripts/seasons/night_looks.py')}
    for p, expected in physical['source_hashes'].items():
        assert digest(ROOT/p) == expected, f'Stale area reference: {p}'
        inputs[p] = expected
    assert [s['key'] for s in physical['seasons']] == [0, 3, 6, 9]
    assert len(physical['results']) == 24
    report = dict(method='Photo-led subtle warmth: C-model relative variation scaled to10% maximum night R/B increase over original patch',
                  limits=['not measured CCT or raw-camera white balance', 'global trial also changes exterior colors; masks not yet applied',
                          'no independent tint correction; clipping can alter tint', 'current WebP is trial input, not final lossless export',
                          'approximate modeled material/weather/exposure affects relative target'],
                  patches=PATCHES, inputs=inputs, model={}, photos={}, outputs={},
                  magick=subprocess.check_output(['magick', '-version'], text=True).splitlines()[0])

    def load(path):
        inputs[str(path.relative_to(ROOT))] = digest(path)
        w, h = map(int, subprocess.check_output(['magick', 'identify', '-format', '%w %h', str(path)]).split())
        raw = subprocess.check_output(['magick', str(path), '-alpha', 'off', '-colorspace', 'RGB', '-depth', '16', '-endian', 'LSB', 'rgb:-'])
        return np.frombuffer(raw, dtype='<u2').reshape(h, w, 3).astype(float)/65535

    sc = bpy.context.scene
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = physical['view_transform']
    # One lower diagnostic exposure avoids fitting warmth from blown-out model paint.
    sc.view_settings.exposure = physical['exposure']-2
    report['model_sampling_exposure'] = sc.view_settings.exposure
    sc.view_settings.gamma = 1
    sc.view_settings.use_white_balance = False
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    sc.render.image_settings.color_depth = '16'

    def component(name):
        path = source/f'{name}.exr'
        assert digest(path) == physical['component_sha256'][path.name], path
        inputs[str(path.relative_to(ROOT))] = digest(path)
        im = bpy.data.images.load(str(path), check_existing=False)
        w, h = im.size
        a = np.array(im.pixels[:], dtype=np.float32).reshape(h, w, 4)
        bpy.data.images.remove(im)
        return a

    for group, views in MODEL_VIEWS.items():
        deltas = []
        for view in views:
            coord_path = source/f'{view}-sample-pixels.json'
            inputs[str(coord_path.relative_to(ROOT))] = digest(coord_path)
            coords = json.loads(coord_path.read_text())
            points = coords['ceiling'] + coords['paint']
            yy, xx = np.array(points).T
            samples = []
            lamps = component(f'{view}-lamps-2700')
            for key in (0, 3, 6, 9):
                a = lamps+component(f'{view}-{key:02d}-daylight')
                a[:, :, :3] = a[:, :, :3] @ np.array(looks['treatments']['C']['knot_matrices'][TIMELINE.index(key)]).T
                a[:, :, 3] = 1
                h, w, _ = a.shape
                im = bpy.data.images.new('C_area_display', w, h, alpha=True, float_buffer=True)
                im.pixels.foreach_set(a.ravel())
                path = OUT/f'model-{view}-{key:02d}-C.png'
                im.save_render(str(path), scene=sc)
                bpy.data.images.remove(im)
                # Ray coordinates use Blender's bottom-origin; decoded images use top-origin.
                samples.append(load(path)[h-1-yy, xx])
            stack = np.array(samples)
            valid = ((stack > .025) & (stack < .95)).all(axis=(0, 2))
            if valid.sum() < 20:
                report['model'][view] = dict(excluded='fewer than20 common unclipped paint samples', common_samples=int(valid.sum()))
                continue
            means = stack[:, valid].mean(axis=1)
            warmth = np.log(means[:, 0]/means[:, 2])
            deltas.append(warmth-warmth[0])
            report['model'][view] = dict(common_samples=int(valid.sum()), display_linear_rgb=means.tolist(), relative_warmth=(warmth-warmth[0]).tolist())
        assert len(deltas) >= 2, f'Insufficient usable reference views: {group}'
        shift = np.mean(deltas, axis=0)
        report['model'][group] = dict(views=views, relative_warmth=shift.tolist())
    shifts = photo_shifts({group: report['model'][group]['relative_warmth'] for group in GROUPS})
    report['photo_shifts'] = shifts
    for group in GROUPS:
        shift = shifts[group]
        rows = []
        for phase_index, key in enumerate((3, 6, 9), 1):
            rows.append(f'<h2 id="phase{key}">{ {3:"Fall",6:"Winter",9:"Spring"}[key]} · phase {key}</h2>')
            rows.append('<table><tr><th>Original · unchanged</th><th>Current seasonal</th><th>Warmth-only trial</th></tr>')
            sheet = ['magick']
            for view in GROUPS[group]:
                original_path = ROOT/f'assets/listing/{view}.webp'
                current_path = ROOT/f'assets/seasons-next/{view}/{key:02d}.webp'
                original, current = load(original_path), load(current_path)
                assert original.shape == current.shape, view
                def sample(image):
                    patches = []
                    for x, y, w, h in PATCHES[view]:
                        assert x+w <= image.shape[1] and y+h <= image.shape[0]
                        patches.append(np.median(image[y:y+h, x:x+w], axis=(0, 1)).tolist())
                    return np.array(reference_rgb(patches)), patches
                orig_mean, original_patches = sample(original)
                src_mean, current_patches = sample(current)
                target = math.log(orig_mean[0]/orig_mean[2])+float(shift[phase_index])
                gains = warmth_gains(src_mean, target)
                adjusted = current*np.array(gains)
                clipping = float((adjusted > 1).any(axis=2).mean())
                adjusted = np.clip(adjusted, 0, 1)
                achieved, achieved_patches = sample(adjusted)
                assert abs(math.log(achieved[0]/achieved[2])-target) < .02, f'Clipped reference: {view}-{key}'
                encoded = np.where(adjusted <= .0031308, 12.92*adjusted, 1.055*adjusted**(1/2.4)-.055)
                filename = f'{view}-{key:02d}-trial.png'
                subprocess.run(['magick', '-size', f'{current.shape[1]}x{current.shape[0]}', '-depth', '16', '-endian', 'LSB', 'rgb:-', '-set', 'colorspace', 'sRGB', str(OUT/filename)],
                               input=np.round(encoded*65535).astype('<u2').tobytes(), check=True)
                tint_delta = math.log(src_mean[1]/math.sqrt(src_mean[0]*src_mean[2]))-math.log(orig_mean[1]/math.sqrt(orig_mean[0]*orig_mean[2]))
                report['photos'][f'{view}-{key:02d}'] = dict(original_patches=original_patches, current_patches=current_patches, achieved_patches=achieved_patches,
                    original_rgb=orig_mean.tolist(), current_rgb=src_mean.tolist(), target_log_rb=target,
                    achieved_rgb=achieved.tolist(), gains=gains, clipped_pixel_fraction=clipping, tint_axis_change_from_original=tint_delta)
                report['outputs'][filename] = digest(OUT/filename)
                originals_url = f'/assets/listing/{view}.webp'
                current_url = f'/assets/seasons-next/{view}/{key:02d}.webp'
                rows.append(f'<tr><th colspan="3">Photo {view} · target R/B {math.exp(target):.2f} (linear RGB) · clipping {clipping:.1%} · tint untouched</th></tr><tr>'+''.join(
                    f'<td><a href="{url}"><img src="{url}" alt="Photo {view}, phase {key}, {label}"></a></td>' for url, label in
                    ((originals_url, 'original'), (current_url, 'current'), (filename, 'trial')))+'</tr>')
                sheet += ['(', str(original_path), str(current_path), str(OUT/filename), '-resize', '440x293!', '+append', ')']
            rows.append('</table>')
            sheet_name = f'{group}-{key:02d}-sheet.jpg'
            subprocess.run([*sheet, '-append', str(OUT/sheet_name)], check=True)
            report['outputs'][sheet_name] = digest(OUT/sheet_name)
        filename = f'{group}.html'
        (OUT/filename).write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Private warmth trial</title>'
            '<style>body{font:16px system-ui;margin:24px;background:#fafafa;color:#222}table{width:100%;table-layout:fixed}img{display:block;width:100%;height:auto}th{text-align:left;padding:8px}p{max-width:1000px;line-height:1.5}</style>'
            f'<h1>{group.replace("-", " ").title()} · C-guided warmth trial</h1>'
            '<p><a href="loft.html">Loft</a> · <a href="great-room.html">Great room</a> · <a href="#phase3">Fall</a> · <a href="#phase6">Winter</a> · <a href="#phase9">Spring</a> · <a href="recipe.json">Recipe</a></p>'
            '<p>Photo-led subtle warmth: maximum night target is10% higher linear red/blue ratio than original, not a Kelvin setting. C-model guides relative room/season variation only; literal model strength was rejected as too orange. Originals unchanged. Shared shift within each area; corrections differ for existing casts. Three white-painted patches per photo, pixel median within each then median across three. No independent tint correction; median reference luminance held. Global trial also changes windows: masking may be needed. Current delivered WebPs are before inputs; all trials private, not approved exports.</p>'
            '<p>Columns: original / current seasonal / proposed warmth. Click image for full size. Model reference sampling uses one fixed exposure two stops below earlier previews to avoid blown-out paint; photo exposure is not lowered. Model geometry, weather and tone mapping limit precision. No new generated scenery.</p>'+''.join(rows)+'</html>')
        report['outputs'][filename] = digest(OUT/filename)
    assert len(report['photos']) == 24
    for path, expected in inputs.items():
        assert digest(ROOT/path) == expected, f'Input changed: {path}'
    (OUT/'recipe.json').write_text(json.dumps(report, indent=2)+'\n')
    print('PASS 24 private warmth-only candidates; source hashes unchanged')


if __name__ == '__main__':
    run()
