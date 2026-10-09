#!/usr/bin/env python3
"""Private warmth-only photo trials. Run with Blender for its installed NumPy.

blender -b --python-exit-code 1 -P scripts/seasons/photo_wb.py
blender -b --python-exit-code 1 -P scripts/seasons/photo_wb.py -- --look B
blender -b --python-exit-code 1 -P scripts/seasons/photo_wb.py -- --kitchen
blender -b --python-exit-code 1 -P scripts/seasons/photo_wb.py -- --interiors
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
KITCHEN_TARGETS = {'05': 'kitchen', '35': 'great-room', '47': 'kitchen', '48': 'kitchen'}
INTERIOR_GROUPS = {'primary-bedroom': ('18', '37'), 'guest-bedroom': ('23', '60'),
                   'powder-room': ('36',), 'upper-bath': ('38',), 'hall': ('49',), 'mudroom': ('54',),
                   'great-room': ('34', '42', '44', '45', '46'), 'loft': ('58', '61'),
                   'back-porch': ('04', '50', '17', '51', '52', '53')}
INTERIOR_MODEL_VIEWS = {'primary-bedroom': ('18', '37'), 'guest-bedroom': ('23', '60'),
                        'powder-room': ('powder-a', 'powder-b'), 'upper-bath': ('bath-a', 'bath-b'),
                        'hall': ('hall-a', 'hall-b'), 'mudroom': ('mud-a', 'mud-b'),
                        'back-porch': ('porch-a', 'porch-b')}
PORCH_WHITE_ANCHORS = ('04', '50')
PORCH_WOOD_PATCHES = {
    '04': ((450, 125, 70, 45), (590, 75, 70, 45), (210, 100, 70, 45)),
    '50': ((750, 100, 70, 40), (820, 180, 70, 40), (650, 60, 70, 40)),
    '17': ((700, 45, 80, 40), (950, 90, 80, 45), (1120, 120, 80, 45)),
    '51': ((420, 60, 90, 45), (680, 95, 90, 45), (920, 140, 90, 45)),
    '52': ((200, 50, 75, 30), (350, 30, 75, 30), (110, 90, 75, 30)),
    '53': ((680, 120, 80, 45), (800, 180, 80, 45), (920, 100, 80, 45)),
}
HELD_INTERIORS = ('30', '73')
ORIGINAL_INTERIORS = ('07', '15', '19', '20', '24', '55', '56')
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
    '05': ((180, 100, 140, 70), (460, 160, 120, 70), (1070, 45, 130, 60)),
    '35': ((200, 260, 100, 70), (810, 190, 90, 75), (1210, 130, 110, 80)),
    '47': ((90, 320, 110, 100), (460, 180, 120, 65), (930, 190, 110, 50)),
    '48': ((380, 80, 130, 70), (450, 210, 130, 50), (220, 370, 70, 110)),
    '18': ((160, 60, 120, 70), (400, 120, 100, 65), (960, 90, 120, 70)),
    '37': ((170, 55, 130, 80), (750, 45, 130, 75), (1130, 110, 130, 70)),
    '23': ((285, 70, 130, 75), (740, 70, 130, 65), (1040, 230, 130, 65)),
    '60': ((250, 65, 130, 75), (790, 70, 130, 75), (1060, 190, 120, 70)),
    '36': ((700, 8, 50, 20), (780, 8, 50, 20), (860, 8, 40, 20)),
    '38': ((580, 8, 70, 16), (790, 8, 120, 20), (1060, 10, 100, 30)),
    '49': ((460, 370, 70, 150), (790, 275, 80, 90), (810, 90, 110, 65)),
    '54': ((880, 250, 120, 120), (1040, 550, 120, 120), (150, 200, 80, 90)),
    '34': ((740, 110, 100, 100), (1120, 460, 110, 110), (410, 220, 80, 55)),
    '42': ((1060, 30, 120, 75), (900, 180, 100, 60), (130, 280, 85, 95)),
    '44': ((75, 255, 100, 70), (550, 150, 100, 80), (650, 50, 90, 70)),
    '45': ((425, 125, 110, 80), (810, 170, 100, 100), (570, 290, 100, 65)),
    '46': ((440, 85, 120, 75), (1150, 80, 100, 60), (1240, 300, 120, 50)),
    '58': ((410, 85, 100, 65), (1080, 235, 120, 65), (520, 430, 80, 50)),
    '61': ((445, 160, 90, 80), (760, 125, 120, 65), (1080, 110, 120, 65)),
    '04': ((610, 795, 25, 10), (670, 757, 25, 10), (730, 720, 25, 10)),
    '50': ((650, 630, 65, 9), (745, 630, 65, 9), (690, 690, 70, 9)),
    **{v: p for v, p in PORCH_WOOD_PATCHES.items() if v not in PORCH_WHITE_ANCHORS},
}


def reference_rgb(patches):
    """Equal-weight per-channel median of three separately sampled paint patches."""
    if len(patches) != 3 or not all(len(p) == 3 and all(math.isfinite(v) and v >= 0 for v in p) for p in patches):
        raise ValueError('Three nonnegative finite RGB patch samples required')
    return tuple(median(p[c] for p in patches) for c in range(3))


def warmth_gains(rgb, target):
    """One log-R/B axis; preserve G/sqrt(RB) and mean reference luminance."""
    if len(rgb) != 3 or not all(math.isfinite(v) and v > 0 for v in rgb) or not math.isfinite(target):
        raise ValueError('Positive finite RGB and finite warmth required')
    delta = target-math.log(rgb[0]/rgb[2])
    gains = (math.exp(delta/2), 1., math.exp(-delta/2))
    scale = luminance(rgb)/luminance(tuple(a*b for a, b in zip(rgb, gains)))
    return tuple(v*scale for v in gains)


def photo_shifts(model_shifts, peak=None):
    """Use saved global peak for new rooms; never normalize each room separately."""
    if peak is None:
        peak = max(v[2] for v in model_shifts.values())
    if not math.isfinite(peak) or peak <= 0:
        raise ValueError('Positive modeled night warmth required')
    return {room: [v*math.log(1.10)/peak for v in values] for room, values in model_shifts.items()}


def look_shifts(base, difference):
    """Keep original anchor and photo-led strength; add only the look difference."""
    if len(base) != 4 or len(difference) != 4 or not all(math.isfinite(v) for v in [*base, *difference]):
        raise ValueError('Four finite base shifts and look differences required')
    return [b+d-difference[0] for b, d in zip(base, difference)]


def probe_gain(rgb):
    """Measure HDR probe chromaticity at a common radiance, not clipped brightness."""
    if len(rgb) != 3 or not all(math.isfinite(v) and v > 0 for v in rgb):
        raise ValueError('Positive finite probe RGB required')
    return float(.1/luminance(rgb))


def reference_usable(rgb):
    """Conservative preview signal/headroom gate, not a calibrated color tolerance."""
    return len(rgb) == 3 and all(math.isfinite(v) and .002 <= v < .98 for v in rgb)


def wood_transfer(anchor_pairs, anchor_holds=()):
    """Median original-relative wood change from two valid, agreeing daybed anchors."""
    if anchor_holds:
        raise ValueError('Daybed anchor held: '+ '; '.join(anchor_holds))
    if len(anchor_pairs) != 2 or any(len(rgb) != 3 or not all(math.isfinite(v) and v > 0 for v in rgb)
                                   for pair in anchor_pairs for rgb in pair) or any(len(pair) != 2 for pair in anchor_pairs):
        raise ValueError('Two positive finite original/adjusted RGB anchor pairs required')
    deltas = [math.log(after[0]/after[2])-math.log(before[0]/before[2]) for before, after in anchor_pairs]
    if max(deltas)-min(deltas) > .2 or min(deltas) < 0 < max(deltas):
        raise ValueError(f'Wood anchors disagree: {deltas}; transfer held')
    return median(deltas)


def run(look='C', kitchen=False, interiors=False):
    import bpy
    import numpy as np
    import subprocess

    assert look in ('B', 'C')
    new_rooms = kitchen or interiors
    assert not new_rooms or look == 'B'
    assert not (kitchen and interiors)
    out = OUT/'interiors-B' if interiors else OUT/'kitchen-B' if kitchen else OUT/'B' if look == 'B' else OUT
    groups = INTERIOR_GROUPS if interiors else {'kitchen': tuple(KITCHEN_TARGETS)} if kitchen else GROUPS
    model_views = INTERIOR_MODEL_VIEWS if interiors else {'kitchen': ('kitchen-west', 'kitchen-south')} if kitchen else MODEL_VIEWS
    out.mkdir(parents=True, exist_ok=True)
    baseline = json.loads((OUT/'recipe.json').read_text()) if look == 'B' else None
    compare_saved_c = baseline is not None and not new_rooms
    source = MODEL/('interiors' if interiors else 'kitchen' if kitchen else 'areas')
    physical = json.loads((source/'results.json').read_text())
    look_path = MODEL/'timeline/looks/recipe.json'
    looks = json.loads(look_path.read_text())
    inputs = {str(p.relative_to(ROOT)): digest(p) for p in (source/'results.json', look_path, Path(__file__), ROOT/'scripts/seasons/night_looks.py')}
    if baseline:
        inputs[str((OUT/'recipe.json').relative_to(ROOT))] = digest(OUT/'recipe.json')
        for name, expected in baseline['outputs'].items():
            path = OUT/name
            assert digest(path) == expected, f'C baseline changed: {path}'
            inputs[str(path.relative_to(ROOT))] = expected
        prior_physical = MODEL/'areas/results.json'
        inputs[str(prior_physical.relative_to(ROOT))] = digest(prior_physical)
        assert digest(prior_physical) == baseline['inputs'][str(prior_physical.relative_to(ROOT))]
        assert digest(look_path) == baseline['inputs'][str(look_path.relative_to(ROOT))]
    if new_rooms:
        approved_path = OUT/'B-reviewed/recipe.json'
        approved = json.loads(approved_path.read_text())
        inputs[str(approved_path.relative_to(ROOT))] = digest(approved_path)
        assert approved['inputs'][str((OUT/'recipe.json').relative_to(ROOT))] == digest(OUT/'recipe.json')
        for name, expected in approved['outputs'].items():
            path = approved_path.parent/name
            assert digest(path) == expected, f'Accepted B changed: {path}'
            inputs[str(path.relative_to(ROOT))] = expected
    for p, expected in physical['source_hashes'].items():
        assert digest(ROOT/p) == expected, f'Stale area reference: {p}'
        inputs[p] = expected
    assert [s['key'] for s in physical['seasons']] == [0, 3, 6, 9]
    assert len(physical['results']) == 4*sum(map(len, model_views.values()))
    report = dict(look=look, method='Photo-led C baseline; B adds matched model B-minus-C warmth without renormalizing the night cap' if baseline else
                  'Photo-led subtle warmth: C-model relative variation scaled to10% maximum night R/B increase over original patch',
                  limits=['not measured CCT or raw-camera white balance', 'global trial also changes exterior colors; masks not yet applied',
                          'no independent tint correction; clipping can alter tint', 'current WebP is trial input, not final lossless export',
                          'approximate modeled material/weather/exposure affects relative target'],
                  patches=PATCHES, inputs=inputs, model={}, photos={}, outputs={},
                  magick=subprocess.check_output(['magick', '-version'], text=True).splitlines()[0])

    def load(path):
        key = str(path.relative_to(ROOT))
        inputs[key] = digest(path)
        if baseline and key in baseline['inputs']:
            assert inputs[key] == baseline['inputs'][key], f'C reference input changed: {path}'
        w, h = map(int, subprocess.check_output(['magick', 'identify', '-format', '%w %h', str(path)]).split())
        raw = subprocess.check_output(['magick', str(path), '-alpha', 'off', '-colorspace', 'RGB', '-depth', '16', '-endian', 'LSB', 'rgb:-'])
        return np.frombuffer(raw, dtype='<u2').reshape(h, w, 3).astype(float)/65535

    sc = bpy.context.scene
    sc.view_settings.view_transform = 'AgX'
    sc.view_settings.look = physical['view_transform']
    # One lower diagnostic exposure avoids fitting warmth from blown-out model paint.
    sc.view_settings.exposure = physical['exposure']-2
    report['model_sampling_exposure'] = sc.view_settings.exposure
    # Warm bathroom blue is valid near .006 linear; .025 rejected every sample.
    sample_floor = .005 if interiors else .025
    report['model_sample_floor'] = sample_floor
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

    for group, views in model_views.items():
        deltas = []
        c_deltas = []
        look_deltas = []
        for view in views:
            coord_path = source/f'{view}-sample-pixels.json'
            inputs[str(coord_path.relative_to(ROOT))] = digest(coord_path)
            coords = json.loads(coord_path.read_text())
            points = coords['probe'] if group == 'back-porch' else coords['ceiling'] + coords['paint']
            yy, xx = np.array(points).T
            samples = []
            c_samples = []
            probe_gains = []
            lamps = component(f'{view}-lamps-2700')
            for key in (0, 3, 6, 9):
                total = lamps+component(f'{view}-{key:02d}-daylight')
                if group == 'back-porch':
                    gain = probe_gain(total[yy, xx, :3].mean(axis=0))
                    total[:, :, :3] *= gain
                    probe_gains.append(gain)
                a = total.copy()
                a[:, :, :3] = a[:, :, :3] @ np.array(looks['treatments'][look]['knot_matrices'][TIMELINE.index(key)]).T
                a[:, :, 3] = 1
                h, w, _ = a.shape
                im = bpy.data.images.new('C_area_display', w, h, alpha=True, float_buffer=True)
                im.pixels.foreach_set(a.ravel())
                path = out/f'model-{view}-{key:02d}-{look}.png'
                im.save_render(str(path), scene=sc)
                bpy.data.images.remove(im)
                # Ray coordinates use Blender's bottom-origin; decoded images use top-origin.
                samples.append(load(path)[h-1-yy, xx])
                if new_rooms:
                    total[:, :, :3] = total[:, :, :3] @ np.array(looks['treatments']['C']['knot_matrices'][TIMELINE.index(key)]).T
                    total[:, :, 3] = 1
                    im = bpy.data.images.new('C_kitchen_display', w, h, alpha=True, float_buffer=True)
                    im.pixels.foreach_set(total.ravel())
                    c_path = out/f'model-{view}-{key:02d}-C.png'
                    im.save_render(str(c_path), scene=sc)
                    bpy.data.images.remove(im)
                    c_samples.append(load(c_path)[h-1-yy, xx])
                elif baseline:
                    c_samples.append(load(OUT/f'model-{view}-{key:02d}-C.png')[h-1-yy, xx])
            stack = np.array(samples)
            valid = ((stack > sample_floor) & (stack < .95)).all(axis=(0, 2))
            if baseline:
                c_stack = np.array(c_samples)
                valid &= ((c_stack > sample_floor) & (c_stack < .95)).all(axis=(0, 2))
            if valid.sum() < 20:
                report['model'][view] = dict(excluded='fewer than20 common unclipped paint samples', common_samples=int(valid.sum()))
                continue
            means = stack[:, valid].mean(axis=1)
            warmth = np.log(means[:, 0]/means[:, 2])
            deltas.append(warmth-warmth[0])
            if baseline:
                c_means = c_stack[:, valid].mean(axis=1)
                c_warmth = np.log(c_means[:, 0]/c_means[:, 2])
                look_deltas.append(warmth-c_warmth)
                c_deltas.append(c_warmth-c_warmth[0])
            report['model'][view] = dict(common_samples=int(valid.sum()), display_linear_rgb=means.tolist(), relative_warmth=(warmth-warmth[0]).tolist())
            if probe_gains:
                report['model'][view]['probe_radiance_gains'] = probe_gains
        assert len(deltas) >= 2, f'Insufficient usable reference views: {group}'
        shift = np.mean(deltas, axis=0)
        report['model'][group] = dict(views=views, relative_warmth=shift.tolist())
        if baseline:
            report['model'][group]['look_difference'] = np.mean(look_deltas, axis=0).tolist()
            report['model'][group]['c_relative_warmth'] = np.mean(c_deltas, axis=0).tolist()
    if new_rooms:
        peak = max(baseline['model'][g]['relative_warmth'][2] for g in GROUPS)
        c_shifts = photo_shifts({g: report['model'][g]['c_relative_warmth'] for g in model_views}, peak=peak)
        shifts = {g: look_shifts(c_shifts[g], report['model'][g]['look_difference']) for g in model_views}
        for g in ({'great-room'} if kitchen else set(groups)-set(model_views)):
            shifts[g] = approved['photo_shifts'][g]
        targets = KITCHEN_TARGETS if kitchen else {v: g for g, views in groups.items() for v in views}
        report.update(global_c_peak=peak, c_photo_shifts=c_shifts, photo_targets=targets)
    else:
        shifts = {group: look_shifts(baseline['photo_shifts'][group], report['model'][group]['look_difference']) for group in groups} if baseline else photo_shifts(
            {group: report['model'][group]['relative_warmth'] for group in groups})
    report['photo_shifts'] = shifts
    for group in groups:
        rows = []
        for phase_index, key in enumerate((3, 6, 9), 1):
            rows.append(f'<h2 id="phase{key}">{ {3:"Fall",6:"Winter",9:"Spring"}[key]} · phase {key}</h2>')
            rows.append('<table><tr><th>Original · unchanged</th><th>'+('C trial' if compare_saved_c else 'Current seasonal')+f'</th><th>{look} warmth-only trial</th></tr>')
            sheet = ['magick']
            porch_anchors = []
            porch_anchor_holds = []
            for view in groups[group]:
                target_area = KITCHEN_TARGETS[view] if kitchen else group
                shift = shifts[target_area]
                original_path = ROOT/f'assets/listing/{view}.webp'
                current_path = ROOT/f'assets/seasons-next/{view}/{key:02d}.webp'
                original, current = load(original_path), load(current_path)
                assert original.shape == current.shape, view
                def sample(image, rectangles=PATCHES[view]):
                    patches = []
                    for x, y, w, h in rectangles:
                        assert x+w <= image.shape[1] and y+h <= image.shape[0]
                        patches.append(np.median(image[y:y+h, x:x+w], axis=(0, 1)).tolist())
                    return np.array(reference_rgb(patches)), patches
                orig_mean, original_patches = sample(original)
                src_mean, current_patches = sample(current)
                transferred = group == 'back-porch' and view not in PORCH_WHITE_ANCHORS
                holds = []
                if interiors and not all(reference_usable(rgb) for rgb in (orig_mean, src_mean)):
                    holds.append('Reference too dark or clipped for reliable color fitting')
                room_shift = float(shift[phase_index])
                if transferred:
                    try:
                        room_shift = wood_transfer(porch_anchors, porch_anchor_holds)
                    except ValueError as exc:
                        holds.append(str(exc))
                unchanged = bool(holds)
                target = None if unchanged else math.log(orig_mean[0]/orig_mean[2])+room_shift
                gains = (1., 1., 1.) if unchanged else warmth_gains(src_mean, target)
                adjusted = current*np.array(gains)
                clipping = float((adjusted > 1).any(axis=2).mean())
                adjusted = np.clip(adjusted, 0, 1)
                achieved, achieved_patches = sample(adjusted)
                if not unchanged:
                    assert abs(math.log(achieved[0]/achieved[2])-target) < .02, f'Clipped reference: {view}-{key}'
                encoded = np.where(adjusted <= .0031308, 12.92*adjusted, 1.055*adjusted**(1/2.4)-.055)
                filename = f'{view}-{key:02d}-trial.png'
                subprocess.run(['magick', '-size', f'{current.shape[1]}x{current.shape[0]}', '-depth', '16', '-endian', 'LSB', 'rgb:-', '-set', 'colorspace', 'sRGB', str(out/filename)],
                               input=np.round(encoded*65535).astype('<u2').tobytes(), check=True)
                if interiors and clipping > .02:
                    holds.append('More than2% newly clipped pixels; highlight review required')
                if interiors and view == '38' and key == 6:
                    holds.append('Visual review: modeled winter target looks excessively warm; owner adjustment needed')
                tint_delta = (math.log(src_mean[1]/math.sqrt(src_mean[0]*src_mean[2]))-math.log(orig_mean[1]/math.sqrt(orig_mean[0]*orig_mean[2]))) if min(*src_mean, *orig_mean) > 0 else None
                report['photos'][f'{view}-{key:02d}'] = dict(target_area=target_area, original_patches=original_patches, current_patches=current_patches, achieved_patches=achieved_patches,
                    original_rgb=orig_mean.tolist(), current_rgb=src_mean.tolist(), target_log_rb=target,
                    achieved_rgb=achieved.tolist(), gains=gains, clipped_pixel_fraction=clipping, tint_axis_change_from_original=tint_delta)
                report['photos'][f'{view}-{key:02d}'].update(reference_kind='daybed-anchored wood transfer' if transferred else 'white paint/daybed',
                    status='HOLD' if holds else 'owner-review-pending', hold_reasons=holds, unchanged_source=unchanged)
                if group == 'back-porch' and view in PORCH_WHITE_ANCHORS:
                    before_wood, _ = sample(original, PORCH_WOOD_PATCHES[view])
                    after_wood, _ = sample(adjusted, PORCH_WOOD_PATCHES[view])
                    porch_anchors.append((before_wood.tolist(), after_wood.tolist()))
                    porch_anchor_holds.extend(f'{view}: {reason}' for reason in holds)
                    if not all(reference_usable(rgb) for rgb in (before_wood, after_wood)):
                        porch_anchor_holds.append(f'{view}: wood reference too dark or clipped')
                    report['photos'][f'{view}-{key:02d}']['wood_reference'] = dict(original=before_wood.tolist(), adjusted=after_wood.tolist())
                report['outputs'][filename] = digest(out/filename)
                originals_url = f'/assets/listing/{view}.webp'
                current_url = f'../{filename}' if compare_saved_c else f'/assets/seasons-next/{view}/{key:02d}.webp'
                status = 'HOLD — '+ '; '.join(holds) if holds else 'Owner review pending'
                rows.append(f'<tr><th colspan="3">Photo {view} · {status} · '+('unchanged source, no fitted target' if unchanged else f'target R/B {math.exp(target):.2f}')+f' · clipping {clipping:.1%} · tint untouched</th></tr><tr>'+''.join(
                    f'<td><a href="{url}"><img src="{url}" alt="Photo {view}, phase {key}, {label}"></a></td>' for url, label in
                    ((originals_url, 'original'), (current_url, 'saved C' if compare_saved_c else 'current'), (filename, 'held unchanged source' if unchanged else f'{look} trial')))+'</tr>')
                sheet += ['(', str(original_path), str(OUT/filename if compare_saved_c else current_path), str(out/filename), '-resize', '440x293!', '+append', ')']
            if group == 'back-porch':
                deltas = [math.log(a[0]/a[2])-math.log(b[0]/b[2]) if min(*a, *b)>0 else None for b, a in porch_anchors]
                transfer = dict(anchors=PORCH_WHITE_ANCHORS, anchor_holds=porch_anchor_holds, wood_pairs=porch_anchors, individual_log_rb=deltas,
                                spread_log_rb=max(deltas)-min(deltas) if None not in deltas else None, maximum_spread=.2)
                try:
                    transfer.update(relative_log_rb=wood_transfer(porch_anchors, porch_anchor_holds), status='owner-review-pending')
                except ValueError as exc:
                    transfer.update(relative_log_rb=None, status='HOLD', reason=str(exc))
                report.setdefault('porch_transfer', {})[str(key)] = transfer
            rows.append('</table>')
            sheet_name = f'{group}-{key:02d}-sheet.jpg'
            subprocess.run([*sheet, '-append', str(out/sheet_name)], check=True)
            report['outputs'][sheet_name] = digest(out/sheet_name)
        filename = f'{group}.html'
        (out/filename).write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Private warmth trial</title>'
            '<style>body{font:16px system-ui;margin:24px;background:#fafafa;color:#222}table{width:100%;table-layout:fixed}img{display:block;width:100%;height:auto}th{text-align:left;padding:8px}p{max-width:1000px;line-height:1.5}</style>'
            f'<h1>{group.replace("-", " ").title()} · {look}-guided warmth trial</h1>'+(
            '<p>B is warmer than C. Columns: original / saved C / new B. B adds the model B-minus-C warmth difference to existing photo-led targets; no new physical simulation or independent tint correction. C copies remain unchanged.</p>' if compare_saved_c else '')+(
            '<p>Columns: original / current seasonal / B trial. Kitchen05/47/48 use new kitchen lighting references with the same saved global C scale plus B-minus-C warmth. Photo35 faces great room and uses its accepted B target. Prior accepted previews unchanged.</p>' if kitchen else '')+
            ('<p>Porch method:04/50 use three white daybed-frame patches. Other views use three shaded cedar patches matched to original wood color, only if both daybed anchors agree. Disagreement over0.2 log R/B or opposite directions holds transfer and leaves source unchanged. Wood is not made white. Porch model uses neutral virtual cards, approximate warm lamps, roof/screen shade and wood bounce. Probe brightness is normalized before fixed AgX color measurement to avoid daytime clipping and unreadable night values; B/C share each gain. This color-only estimate is not a photo exposure adjustment or calibrated photometry.</p>' if group == 'back-porch' else '')+
            '<p>'+('<a href="index.html">All interiors</a> · ' if interiors else '' if kitchen else '<a href="loft.html">Loft</a> · <a href="great-room.html">Great room</a> · ')+'<a href="#phase3">Fall</a> · <a href="#phase6">Winter</a> · <a href="#phase9">Spring</a> · <a href="recipe.json">Recipe</a></p>'
            '<p>C baseline maximum night target is10% higher linear red/blue ratio than original, not a Kelvin setting. B adds warmth beyond that baseline. C-model guides relative room/season variation only; literal model strength was rejected as too orange. Originals unchanged. Shared shift within each area; corrections differ for existing casts. Three reference patches per photo, pixel median within each then median across three; white paint/daybed except explicitly labeled porch wood transfer. No independent tint correction; median reference luminance held. Global trial also changes windows: masking may be needed. Current delivered WebPs are before inputs; all trials private, not approved exports.</p>'
            '<p>Click image for full size. Model reference sampling uses one fixed exposure two stops below earlier previews to avoid blown-out paint; photo exposure is not lowered. Model geometry, weather and tone mapping limit precision. No new generated scenery.</p>'+''.join(rows)+'</html>')
        report['outputs'][filename] = digest(out/filename)
    if interiors:
        accepted = [('Loft21/22/57/59', 'B-reviewed/loft.html'),
                    ('Great room02/12/13/14', 'B-reviewed/great-room.html'),
                    ('Kitchen05/35/47/48', 'kitchen-B-reviewed/kitchen.html')]
        for folder in ('B-reviewed', 'kitchen-B-reviewed'):
            recipe_path = OUT/folder/'recipe.json'
            inputs[str(recipe_path.relative_to(ROOT))] = digest(recipe_path)
            for name, expected in json.loads(recipe_path.read_text())['outputs'].items():
                path = OUT/folder/name
                assert digest(path) == expected, f'Accepted output changed: {path}'
                inputs[str(path.relative_to(ROOT))] = expected
        held = ['<!doctype html><html lang="en"><meta charset="utf-8"><title>Basement held</title>',
                '<style>body{font:16px system-ui;margin:24px}img{width:24%;height:auto}</style>',
                '<h1>Basement30/73 · held, not warmth-adjusted</h1><p><a href="index.html">All interiors</a></p>',
                '<p>No usable basement lighting model or validated three-white-patch fit. No invented targets. Photo73 also needs the previously requested clutter/paving repair. Columns: original / current fall / current winter / current spring.</p>']
        for view in HELD_INTERIORS:
            held.append(f'<h2>Photo {view}</h2>')
            for key in (0, 3, 6, 9):
                path = ROOT/(f'assets/listing/{view}.webp' if key==0 else f'assets/seasons-next/{view}/{key:02d}.webp')
                inputs[str(path.relative_to(ROOT))] = digest(path)
                held.append(f'<img src="/{path.relative_to(ROOT)}" alt="Photo {view}, phase {key}, unchanged current source">')
        held.append('</html>')
        (out/'basement-held.html').write_text(''.join(held))
        index = ['<!doctype html><html lang="en"><meta charset="utf-8"><title>Interior and porch B review</title>',
                 '<style>body{font:18px system-ui;max-width:1000px;margin:32px;line-height:1.6}li{margin:8px 0}</style>',
                 '<h1>Interior and porch B review · all room groups</h1>',
                 '<p>Fall3, winter6, spring9 anchor previews. B is shared style, not shared room temperature or seasonal swing. New rooms use separate daylight/lamp simulations and the saved global photographic scale. Three white ceiling/paint patch medians indoors; porch daybed whites anchor original-relative wood balancing. Colored walls and wood preserved, no independent tint correction or default window masks. Original/current/B columns. Private previews only; intermediate phases and full transition QA remain open.</p>',
                 '<h2>New comparisons · 21 photos / 63 anchors, including holds</h2><ul>']
        index += [f'<li><a href="{g}.html">{g.replace("-", " ").title()} · {" / ".join(views)}</a></li>' for g, views in groups.items()]
        index += ['</ul><h2>Held candidate checks</h2><ul>']
        index += [f'<li><a href="{p["target_area"]}.html#phase{int(name.split("-")[1])}">{name}</a>: '+ '; '.join(p['hold_reasons'])+'</li>'
                  for name, p in report['photos'].items() if p['status']=='HOLD']
        index += ['</ul><h2>Previously accepted · unchanged snapshots</h2><ul>']
        index += [f'<li><a href="../{url}">{label}</a></li>' for label, url in accepted]
        index += ['</ul><h2>Held · 2 basement photos</h2><p><a href="basement-held.html">30 / 73: current anchors, no WB trial</a>. Missing usable model;73 content repair remains open.</p>',
                  '<h2>Unchanged original/gallery interiors · 7 photos</h2><p>These have no changing seasonal treatment; no new variants.</p><ul>']
        for view in ORIGINAL_INTERIORS:
            path = ROOT/f'assets/listing/{view}.webp'
            inputs[str(path.relative_to(ROOT))] = digest(path)
            index.append(f'<li><a href="/assets/listing/{view}.webp">Original {view}</a></li>')
        index += ['</ul><p>Screened porch included; open decks remain outside this batch. Factual plan31 unchanged. <a href="recipe.json">Numerical recipe</a></p></html>']
        (out/'index.html').write_text(''.join(index))
        for name in ('index.html', 'basement-held.html'):
            report['outputs'][name] = digest(out/name)
        report.update(held=HELD_INTERIORS, original_only=ORIGINAL_INTERIORS)
    assert len(report['photos']) == 3*sum(map(len, groups.values()))
    for path, expected in inputs.items():
        assert digest(ROOT/path) == expected, f'Input changed: {path}'
    (out/'recipe.json').write_text(json.dumps(report, indent=2)+'\n')
    print(f'PASS {len(report["photos"])} private comparisons; {sum(p["status"]=="HOLD" for p in report["photos"].values())} held; source hashes unchanged')


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    if args not in ([], ['--look', 'B'], ['--kitchen'], ['--interiors']):
        raise SystemExit('Use Blender with no arguments for C, -- --look B, -- --kitchen or -- --interiors')
    run('B' if args else 'C', kitchen=args == ['--kitchen'], interiors=args == ['--interiors'])
