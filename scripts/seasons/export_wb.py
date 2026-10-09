#!/usr/bin/env python3
"""Prepare approved warmth exports privately; --apply installs locally, --check verifies.

Uses frozen pre-correction sources, never stacks corrections. No generation/deployment.
"""
import argparse
from array import array
from bisect import bisect_right
import json
import math
from pathlib import Path
import shutil
from statistics import median
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from photo_wb import ROOT, OUT as REVIEWS, reference_rgb, reference_usable, warmth_gains
from night_looks import digest

OUT = REVIEWS/'export'
DELIVERY = ROOT/'assets/seasons-next'
FOLDERS = ('B-reviewed', 'kitchen-B-reviewed', 'interiors-B')
CLIPPING_ACCEPTED = {'36-03', '37-06'}
CLIPPING_REASON = 'More than2% newly clipped pixels; highlight review required'


def interpolate_target(key, knots, values):
    if (len(values) != 4 or not all(math.isfinite(v) for v in values)
            or not all(math.isfinite(k) for k in knots)
            or any(b <= a for a, b in zip(knots, knots[1:]))
            or not knots or knots[0] != 0 or knots[-1] != 12
            or any(k not in knots for k in (0, 3, 6, 9, 12)) or key not in knots):
        raise ValueError('Finite four-anchor targets and ordered shared annual knots required')
    anchors = [knots.index(k) for k in (0, 3, 6, 9, 12)]
    values = [*values, values[0]]
    position = knots.index(key)
    if position in anchors:
        return values[anchors.index(position)]
    i = bisect_right(anchors, position)-1
    t = (position-anchors[i])/(anchors[i+1]-anchors[i])
    return values[i]*(1-t)+values[i+1]*t


def select_photos(recipes):
    selected = {}
    seen = set()
    for folder, recipe in recipes.items():
        views = {name.split('-')[0] for name in recipe['photos']}
        for view in sorted(views):
            if not (len(view) == 2 and view.isdigit()) or view in seen:
                raise ValueError('Invalid or duplicate photo reference: '+view)
            seen.add(view)
            names = [f'{view}-{k:02d}' for k in (3, 6, 9)]
            if any(name not in recipe['photos'] for name in names):
                raise ValueError('Three reviewed anchors required: '+view)
            records = [recipe['photos'][name] for name in names]
            if any(p.get('unchanged_source') or p['target_log_rb'] is None or
                   (p.get('status') == 'HOLD' and not (name in CLIPPING_ACCEPTED and p['hold_reasons'] == [CLIPPING_REASON]))
                   for name, p in zip(names, records)):
                continue
            selected[view] = folder
    return selected


def jobs(manifest, selected):
    for number, photo in manifest['photos'].items():
        view = number.zfill(2)
        if view in selected:
            for key in photo['keys']:
                if key not in photo.get('original', []):
                    yield view, key


def label(key):
    if not math.isfinite(key) or key < 0 or key >= 12 or key*2 != int(key*2):
        raise ValueError('Invalid frame key')
    return f'{int(key):02d}'+('h' if key % 1 else '')


def load(path):
    return json.loads(path.read_text(), parse_constant=lambda v: (_ for _ in ()).throw(ValueError(v)))


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')
    temporary.replace(path)


def command(*args):
    return subprocess.check_output([str(a) for a in args])


def size(path):
    return tuple(map(int, command('magick', 'identify', '-format', '%w %h', path).split()))


def sample(path, patches):
    width, height = size(path)
    samples = []
    for x, y, w, h in patches:
        if min(x, y) < 0 or min(w, h) <= 0 or x+w > width or y+h > height:
            raise ValueError('Reference outside image: '+str(path))
        raw = command('magick', path, '-crop', f'{w}x{h}+{x}+{y}', '+repage', '-alpha', 'off',
                      '-colorspace', 'RGB', '-depth', '16', '-endian', 'LSB', 'rgb:-')
        pixels = array('H', raw)
        if sys.byteorder != 'little':
            pixels.byteswap()
        if len(pixels) != w*h*3:
            raise ValueError('Incomplete reference pixels')
        samples.append(tuple(median(pixels[c::3])/65535 for c in range(3)))
    rgb = reference_rgb(samples)
    if not reference_usable(rgb):
        raise ValueError('Unusable frame reference: '+str(path))
    return rgb


def snapshot():
    if not (OUT/'inputs.json').exists():
        OUT.mkdir(parents=True, exist_ok=True)
        recipes = {folder: load(REVIEWS/folder/'recipe.json') for folder in FOLDERS}
        selected = select_photos(recipes)
        # Refuse a partial snapshot instead of silently replacing recovery evidence.
        shutil.copytree(DELIVERY, OUT/'source')
        state = dict(source={str(p.relative_to(DELIVERY)): digest(p) for p in DELIVERY.rglob('*') if p.is_file()},
                     originals={str(p.relative_to(ROOT)): digest(p) for p in (ROOT/'assets/listing').glob('*.webp')}, recipes={}, anchors={})
        for folder, recipe in recipes.items():
            path = OUT/'recipes'/folder/'recipe.json'
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(REVIEWS/folder/'recipe.json', path)
            state['recipes'][folder] = digest(path)
        for view, folder in selected.items():
            recipe = recipes[folder]
            for phase in (3, 6, 9):
                for path in (f'assets/listing/{view}.webp', f'assets/seasons-next/{view}/{phase:02d}.webp'):
                    if digest(ROOT/path) != recipe['inputs'][path]:
                        raise ValueError('Reviewed photographic input changed: '+path)
                name = f'{view}-{phase:02d}-trial.png'
                source = REVIEWS/folder/name
                if digest(source) != recipe['outputs'][name]:
                    raise ValueError('Reviewed anchor changed: '+name)
                shutil.copy2(source, OUT/'recipes'/folder/name)
                state['anchors'][f'{folder}/{name}'] = digest(source)
        save(OUT/'inputs.json', state)
    state = load(OUT/'inputs.json')
    for path, expected in state['source'].items():
        if digest(OUT/'source'/path) != expected:
            raise ValueError('Frozen source changed: '+path)
    for path, expected in state['originals'].items():
        if digest(ROOT/path) != expected:
            raise ValueError('Original/gallery changed: '+path)
    for folder, expected in state['recipes'].items():
        if digest(OUT/'recipes'/folder/'recipe.json') != expected:
            raise ValueError('Frozen recipe changed: '+folder)
    for path, expected in state['anchors'].items():
        if digest(OUT/'recipes'/path) != expected:
            raise ValueError('Frozen anchor changed: '+path)
    return state


def verify_candidates(state, report):
    manifest = load(OUT/'source/frames.json')
    recipes = {folder: load(OUT/'recipes'/folder/'recipe.json') for folder in FOLDERS}
    frames = {f'{view}/{label(key)}' for view, key in jobs(manifest, select_photos(recipes))}
    expected = {f'{name}{suffix}.webp' for name in frames for suffix in ('', '-small')}
    if set(report['outputs']) != expected or set(report['frames']) != frames:
        raise ValueError('Prepared export scope does not match approved manifest frames')
    if report['processor_sha256'] != digest(Path(__file__)) or report['inputs_sha256'] != digest(OUT/'inputs.json'):
        raise ValueError('Prepared batch is stale; prepare again')
    for path, expected in report['outputs'].items():
        if digest(OUT/'candidates'/path) != expected:
            raise ValueError('Candidate changed: '+path)
    for path, before in state['source'].items():
        if digest(DELIVERY/path) not in (before, report['outputs'].get(path, before)):
            raise ValueError('Unexpected local seasonal change: '+path)


def prepare(state):
    manifest = load(OUT/'source/frames.json')
    recipes = {folder: load(OUT/'recipes'/folder/'recipe.json') for folder in FOLDERS}
    selected = select_photos(recipes)
    previous = load(OUT/'report.json') if (OUT/'report.json').exists() else {'outputs': {}}
    for path, before in state['source'].items():
        if digest(DELIVERY/path) not in (before, previous['outputs'].get(path, before)):
            raise ValueError('Unexpected local seasonal change: '+path)
    report = dict(processor_sha256=digest(Path(__file__)), inputs_sha256=digest(OUT/'inputs.json'),
                  method='Reviewed PNG anchors; other frames fit interpolated log-R/B targets on elapsed shared-clock segments',
                  limits=['Frozen WebP-derived photographic inputs, not recovered raw detail', 'Global warmth only; no independent tint or window masks',
                          'No exhaustive transition or generative-fidelity certification'],
                  held_photos=['17', '51', '52', '53', '30', '73'], owner_reviewed_clipping=sorted(CLIPPING_ACCEPTED),
                  frames={}, outputs={})
    rows = []
    for view, key in jobs(manifest, selected):
        folder = selected[view]
        recipe = recipes[folder]
        name = f'{view}/{label(key)}'
        src = OUT/'source'/f'{name}.webp'
        master = OUT/'masters'/f'{name}.png'
        large = OUT/'candidates'/f'{name}.webp'
        small = OUT/'candidates'/f'{name}-small.webp'
        master.parent.mkdir(parents=True, exist_ok=True)
        large.parent.mkdir(parents=True, exist_ok=True)
        anchor = recipe['photos'].get(f'{view}-{label(key)}')
        if anchor:
            reference = OUT/'recipes'/folder/f'{view}-{label(key)}-trial.png'
            shutil.copy2(reference, master)
            target, gains, clipping = anchor['target_log_rb'], anchor['gains'], anchor['clipped_pixel_fraction']
            patches = anchor.get('reference_patches', recipe['patches'][view])
        else:
            patches = recipe['patches'][view]
            original = sample(ROOT/f'assets/listing/{view}.webp', patches)
            values = [math.log(original[0]/original[2])]+[recipe['photos'][f'{view}-{phase:02d}']['target_log_rb'] for phase in (3, 6, 9)]
            target = interpolate_target(key, manifest['knots'], values)
            gains = warmth_gains(sample(src, patches), target)
            matrix = f'{gains[0]} 0 0 0 {gains[1]} 0 0 0 {gains[2]}'
            transform = ['magick', src, '-alpha', 'off', '-colorspace', 'RGB', '-color-matrix', matrix]
            clipping = float(command(*transform, '-separate', '-evaluate-sequence', 'Max', '-threshold', '100%', '-format', '%[fx:mean]', 'info:'))
            ceiling = max(.02, max(recipe['photos'][f'{view}-{p:02d}']['clipped_pixel_fraction'] for p in (3, 6, 9)))+.005
            if clipping > ceiling:
                raise ValueError(f'Unreviewed intermediate clipping: {name}: {clipping:.3%}')
            command(*transform, '-clamp', '-colorspace', 'sRGB', '-depth', '16', master)
        achieved = sample(master, patches)
        if abs(math.log(achieved[0]/achieved[2])-target) >= .02:
            raise ValueError('Output misses reference target: '+name)
        command('magick', master, '-strip', '-quality', '80', large)
        sw, sh = size(ROOT/f'assets/listing/{view}-small.webp')
        command('magick', large, '-resize', f'{sw}x{sh}!', '-strip', '-quality', '78', small)
        if size(large) != size(src) or size(src) != size(ROOT/f'assets/listing/{view}.webp') or size(small) != (sw, sh):
            raise ValueError('Dimension drift: '+name)
        metric = subprocess.run(['magick', 'compare', '-metric', 'RMSE', str(master), str(large), 'null:'], capture_output=True, text=True)
        if metric.returncode not in (0, 1):
            raise RuntimeError(metric.stderr)
        rmse = float(metric.stderr.split('(')[-1].split(')')[0])
        if rmse > .035:
            raise ValueError('Unexpected encoding loss: '+name)
        report['frames'][name] = dict(anchor=bool(anchor), recipe=folder, source_sha256=digest(src), master_sha256=digest(master),
            target_log_rb=target, reference_patches=patches, gains=gains, clipping=clipping, encoding_rmse=rmse,
            dimensions=size(large), small_dimensions=(sw, sh), before_bytes=src.stat().st_size, after_bytes=large.stat().st_size)
        for path in (large, small):
            report['outputs'][str(path.relative_to(OUT/'candidates'))] = digest(path)
        rows.append(f'<h2>Photo{view} · phase{key} · {"approved anchor" if anchor else "interpolated target"}</h2><div>'
                    f'<img src="source/{name}.webp" alt="Photo{view} phase{key} before"><img src="candidates/{name}.webp" alt="Photo{view} phase{key} corrected"></div>')
    save(OUT/'report.json', report)
    (OUT/'review.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><title>Approved warmth exports</title>'
        '<style>body{font:16px system-ui;margin:24px}div{display:flex}img{width:50%;height:auto}</style>'
        '<h1>Approved warmth exports · before / corrected</h1><p>Frozen before source at left; locally prepared export at right. '
        'Original/gallery images unchanged. No deployment. Unreliable porch transfers and basement excluded.</p>'+''.join(rows)+'</html>')
    verify_candidates(state, report)
    return report


def run():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group()
    action.add_argument('--apply', action='store_true')
    action.add_argument('--check', action='store_true')
    args = parser.parse_args()
    if (args.apply or args.check) and not (OUT/'inputs.json').exists():
        raise ValueError('No prepared snapshot; run without flags first')
    state = snapshot()
    report = load(OUT/'report.json') if args.apply or args.check else prepare(state)
    verify_candidates(state, report)
    if args.apply:
        for path in report['outputs']:
            target = DELIVERY/path
            temporary = target.with_suffix('.wb-tmp')
            shutil.copy2(OUT/'candidates'/path, temporary)
            temporary.replace(target)
    if args.apply or args.check:
        for path, before in state['source'].items():
            if digest(DELIVERY/path) != report['outputs'].get(path, before):
                raise ValueError('Installed export mismatch: '+path)
    print(f'PASS {len(report["frames"])} frames / {len(report["outputs"])} exports; '+('installed and verified' if args.apply or args.check else 'prepared privately'))


if __name__ == '__main__':
    run()
