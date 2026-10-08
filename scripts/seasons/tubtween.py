#!/usr/bin/env python3
"""Hot tub: redo first snow's re-light without the winter reference, then real half-step frames by cleaning up the dissolve of the two neighbors."""
import pilot, smooth, subprocess, json, sys, base64, os, urllib.request
from concurrent.futures import ThreadPoolExecutor
f = lambda k: f'fin/06/{k}.final.png'
def part(p):
    d = subprocess.run(['magick', p, '-filter', 'Lanczos', '-resize', '2400x1792!', 'png:-'], check=True, capture_output=True).stdout
    return {'inlineData': {'mimeType': 'image/png', 'data': base64.b64encode(d).decode()}}
def strip(src, k, dst):
    w = int(round(100 * (k if k <= 6 else 12 - k) / 6))
    subprocess.run(['magick', f('00'), f('06'), '-compose', 'blend', '-define', f'compose:args={w}', '-composite', f'/tmp/claude-501/st{k}.png'], check=True)
    subprocess.run(['magick', src, f'/tmp/claude-501/st{k}.png', 'tub/strip-mask2.png', '-compose', 'Over', '-composite', dst], check=True)
def first_snow():
    base = 'tub/o05.png'; out = 'tub/M05'
    P = ('Perform a LIGHTING-ONLY re-light of IMAGE 1, a photograph of a hot tub on a deck. Treat IMAGE 1 as a locked pixel canvas: every object, tree, the framing and the swirling water stay exactly where and as they are. '
         'The amount of snow is exactly what IMAGE 1 shows and no more: a thin first dusting with the deck boards showing through. Do not add snow.\n\n'
         'Change only the light, sky and exposure to deep dusk about forty-five minutes after sunset in early December. The sky is deep blue with the first few faint stars. The scene is dark and cool, a step short of night, and stays easy to read.\n'
         'Three lights are on, at about three quarters of their full night strength: the hot tub water glows blue-cyan from soft submerged points low along its walls; the vertical light strip on the cabinet corner glows blue; and a soft warm lamplight falls on the deck boards at the right, with a weaker warm fill on the boards at the front left. The warm lights never reach the trees. Keep the trees as crisp and natural as in IMAGE 1.\n\nReturn ONE full-frame photograph.')
    body = {'contents': [{'role': 'user', 'parts': [{'text': P}, part(base)]}], 'generationConfig': {'responseModalities': ['IMAGE'], 'imageConfig': {'aspectRatio': '4:3', 'imageSize': '2K'}, 'thinkingConfig': {'thinkingLevel': 'High'}}}
    req = urllib.request.Request('https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent', data=json.dumps(body).encode(), headers={'x-goog-api-key': os.environ['GEMINI_API_KEY'], 'Content-Type': 'application/json'})
    r = json.load(urllib.request.urlopen(req, timeout=400))
    raw = next(base64.b64decode(p['inlineData']['data']) for c in r['candidates'] for p in c['content']['parts'] if 'inlineData' in p)
    open(out + '-raw.png', 'wb').write(raw); subprocess.run(['magick', out + '-raw.png', '-filter', 'Lanczos', '-resize', '1600x1205!', out + '-full.png'], check=True)
    j = json.loads(subprocess.run([sys.executable, 'align.py', base, out + '-full.png', out + '.png'], capture_output=True, text=True).stdout or '{}')
    strip(out + '.png', 5, f('05')); print('first snow re-light: shift', j.get('max_shift_px'), j.get('inliers'), '/', j.get('patches'), flush=True)
NOTE = {
 4.5: 'Late November dusk. Most leaves are now down; the last brown leaves cling. The frost on the boards and rails is a little heavier than in IMAGE 2. There is no snow yet.',
 5.5: 'Late December, nearly night. The snow on the boards and rails is a thin, even layer: more than the first dusting of IMAGE 2, less than the full layer of IMAGE 3.',
 6.5: 'Early February, dark pre-dawn. The snow layer of IMAGE 2 has begun to melt: it is thinner and grainy, and the first wet bare patches of board have opened near the tub, along the wall and where people walk. No loose chunks yet.',
 7.5: 'Early March, dawn twilight. Almost all the snow is gone: only a few small, shrinking remnants of ice remain at the foot of the railing and beside the steps. The boards are wet.',
 8.5: 'Early April, just after sunrise. The deck is dry. The buds have opened into a first thin haze of tiny pale-green leaves, far fewer than in IMAGE 3.',
 9.5: 'Early May, morning. The leaves are fuller and a slightly deeper green than in IMAGE 2, not yet the full canopy of IMAGE 3.',
}
def tween(h):
    lo, hi = int(h), int(h) + 1; A, B = f(f'{lo:02d}'), f(f'{hi:02d}'); s = f'tub/H{lo:02d}'; blend = s + '-blend.png'
    subprocess.run(['magick', A, B, '-evaluate-sequence', 'Mean', blend], check=True)
    P = ('IMAGE 1 is an exact 50% double exposure of two approved photographs of the same hot tub deck from a locked camera: IMAGE 2, taken earlier in the year, and IMAGE 3, taken later. '
         'Turn IMAGE 1 into ONE clean, sharp, single-exposure photograph of the moment halfway between them. This is a clean-up of IMAGE 1, not a new picture. '
         'Keep IMAGE 1 exactly as it is in composition, geometry, overall brightness, color balance and sky. The hot tub, its glowing water, its light strip, the steps, towels, table, railing, wall and every trunk and branch stay at their coordinates. '
         'Change only what is needed to remove the ghosting: where IMAGE 1 shows two faint overlaid versions of something (leaves over bare branches, half-transparent snow or frost, doubled shadows, a half-transparent plant), replace them with one solid, physically plausible in-between state. Where IMAGE 2 and IMAGE 3 agree, leave IMAGE 1 untouched. Add nothing that is in neither. '
         f'The moment: {NOTE[h]} Do not brighten, darken or re-light the picture. Return ONE full-frame photograph.')
    for attempt in (1, 2):
        raw, u = pilot.call([{'text': P}, pilot.img_part(blend, pilot.CANVAS['4:3']), pilot.img_part(A), pilot.img_part(B)], '4:3'); open(s + '-raw.jpg', 'wb').write(raw)
        subprocess.run(['magick', s + '-raw.jpg', '-resize', '1600x1205!', s + '-full.png'], check=True)
        j = json.loads(subprocess.run([sys.executable, 'align.py', blend, s + '-full.png', s + '.png'], capture_output=True, text=True).stdout or '{}')
        if j.get('inliers', 0) >= 20: break
    os.makedirs(s + '-tmp', exist_ok=True); det, off, ab = smooth.score(A, s + '.png', B, tmp=s + '-tmp')
    strip(s + '.png', h, f(f'{lo:02d}h')); subprocess.run(['magick', f(f'{lo:02d}h'), '-quality', '88', f'review/img/06/{lo:02d}h.webp'], check=True)
    print(h, 'shift', j.get('max_shift_px'), j.get('inliers'), '/', j.get('patches'), 'detour', det, flush=True)
first_snow(); subprocess.run(['magick', f('05'), '-quality', '88', 'review/img/06/05.webp'], check=True)
with ThreadPoolExecutor(6) as ex: list(ex.map(tween, list(NOTE)))
